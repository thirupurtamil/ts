



import requests
import pandas as pd
from datetime import date, datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.views.generic import TemplateView

from .models import NiftyExpiry, NiftyOptionSnapshot
from .serializers import NiftyExpirySerializer

# ------------------------
# Helper: fetch NSE JSON
# ------------------------
def fetch_nse_nifty_json():
    headers = {'User-Agent': 'Mozilla/5.0'}
    with requests.Session() as req:
        req.get("https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY", headers=headers)
        res = req.get("https://www.nseindia.com/api/quote-derivative?symbol=NIFTY", headers=headers)
        res.raise_for_status()
        return res.json()


# ==============================================
# 1️⃣ Fetch & Save (Order preserved, same-day delete)
# ==============================================
class NiftyFetchView(APIView):
    """
    GET -> fetch from NSE, save snapshots.
    Logic:
     - preserve NSE JSON order
     - only first 9 expiries processed
     - up to first 14 rows per expiry stored
     - if same-day data exists -> delete then insert fresh (no mixing)
     - new day -> fresh entries (old days preserved)
    """

    def get(self, request):
        today = date.today()
        try:
            payload = fetch_nse_nifty_json()
            stocks = payload.get('stocks', [])
            if not stocks:
                return Response({"error": "No option data from NSE"}, status=status.HTTP_204_NO_CONTENT)

            # collect raw rows in NSE order
            rows = []
            for item in stocks:
                meta = item.get('metadata', {})
                trade = item.get('marketDeptOrderBook', {}).get('tradeInfo', {})
                other = item.get('marketDeptOrderBook', {}).get('otherInfo', {})
                rows.append({
                    "Expiry": meta.get("expiryDate"),
                    "Strike": meta.get("strikePrice"),
                    "Option": meta.get("optionType"),
                    "Open": meta.get("openPrice"),
                    "High": meta.get("highPrice"),
                    "Low": meta.get("lowPrice"),
                    "Close": meta.get("closePrice"),
                    "LTP": meta.get("lastPrice"),
                    "Volume": meta.get("numberOfContractsTraded"),
                    "Value": meta.get("totalTurnover"),
                    "OpenInterest": trade.get("openInterest"),
                    "IV": other.get("impliedVolatility"),
                })

            df = pd.DataFrame(rows)
            if df.empty:
                return Response({"error": "No data after parsing"}, status=status.HTTP_204_NO_CONTENT)

            # preserve NSE expiry order and take first 9 expiries
            expiry_list = list(pd.unique(df['Expiry']))[:9]

            total_created = 0
            seq_counter = 1

            with transaction.atomic():
                for exp in expiry_list:
                    expiry_date = datetime.strptime(exp, "%d-%b-%Y").date()
                    expiry_obj, _ = NiftyExpiry.objects.get_or_create(expiry_date=expiry_date)

                    # delete same-day entries for this expiry to avoid mix
                    NiftyOptionSnapshot.objects.filter(expiry=expiry_obj, fetch_date=today).delete()

                    subset = df[df['Expiry'] == exp].head(14)  # first 14 rows per expiry

                    objs = []
                    for _, r in subset.iterrows():
                        objs.append(NiftyOptionSnapshot(
                            expiry=expiry_obj,
                            fetch_date=today,
                            strike=r['Strike'],
                            option_type=r['Option'],
                            sequence=seq_counter,
                            open_price=r['Open'],
                            high_price=r['High'],
                            low_price=r['Low'],
                            close_price=r['Close'],
                            last_price=r['LTP'],
                            volume=r['Volume'],
                            value=r['Value'],
                            open_interest=r['OpenInterest'],
                            iv=r['IV'],
                        ))
                        seq_counter += 1

                    NiftyOptionSnapshot.objects.bulk_create(objs)
                    total_created += len(objs)

            return Response({
                "message": f"{total_created} records stored (order preserved)",
                "expiries_processed": expiry_list
            }, status=status.HTTP_200_OK)

        except requests.HTTPError as he:
            return Response({"error": f"NSE HTTP error: {str(he)}"}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================
# 2️⃣ Fetch data by fetch_date (API used by frontend)
# ==============================================
class NiftyByFetchDateView(APIView):
    def get(self, request):
        fetch_date = request.query_params.get("fetch_date")
        if not fetch_date:
            return Response({"error": "fetch_date parameter required (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_obj = datetime.strptime(fetch_date, "%Y-%m-%d").date()
        except:
            return Response({"error": "Invalid date format (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)

        snapshots = NiftyOptionSnapshot.objects.filter(fetch_date=date_obj).order_by('sequence')
        if not snapshots.exists():
            return Response({"message": "No data found for given date"}, status=status.HTTP_404_NOT_FOUND)

        expiry_ids = snapshots.values_list('expiry_id', flat=True).distinct()
        expiries = NiftyExpiry.objects.filter(id__in=expiry_ids).order_by('expiry_date')
        serializer = NiftyExpirySerializer(expiries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==============================================
# 3️⃣ Simple endpoints for dropdowns and data
# ==============================================
class ExpiryListAPI(APIView):
    def get(self, request):
        expiries = NiftyExpiry.objects.order_by('expiry_date').values_list('expiry_date', flat=True)
        return Response({"expiries": list(expiries)})


class FetchDateListAPI(APIView):
    def get(self, request, expiry_date):
        fetch_dates = (
            NiftyOptionSnapshot.objects
            .filter(expiry__expiry_date=expiry_date)
            .order_by('fetch_date')
            .values_list('fetch_date', flat=True)
            .distinct()
        )
        return Response({"fetch_dates": list(fetch_dates)})


class NiftyDataAPI(APIView):
    def get(self, request):
        expiry_date = request.GET.get('expiry_date')
        fetch_date = request.GET.get('fetch_date')

        if not expiry_date or not fetch_date:
            return Response({"error": "expiry_date & fetch_date required"}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            NiftyOptionSnapshot.objects
            .filter(expiry__expiry_date=expiry_date, fetch_date=fetch_date)
            .order_by('sequence')
        )

        data = [
            {
                "strike": q.strike,
                "option": q.option_type,
                "open": q.open_price,
                "high": q.high_price,
                "low": q.low_price,
                "close": q.close_price,
                "ltp": q.last_price,
                "volume": q.volume,
                "value": q.value,
                "oi": q.open_interest,
                "iv": q.iv,
            }
            for q in qs
        ]

        return Response({
            "expiry": expiry_date,
            "fetch_date": fetch_date,
            "rows": data
        })


# ==============================================
# 4️⃣ Cleanup expired expiries (optional)
# ==============================================
class ExpiryCleanupView(APIView):
    def delete(self, request):
        today = date.today()
        expired = NiftyExpiry.objects.filter(expiry_date__lt=today)
        if not expired.exists():
            return Response({"message": "No expired expiries"}, status=status.HTTP_200_OK)
        count = expired.count()
        expired.delete()
        return Response({"message": f"Deleted {count} expired expiries"}, status=status.HTTP_200_OK)


# ==============================================
# 5️⃣ Dashboard Template
# ==============================================
class NiftyDashboardView(TemplateView):
    template_name = "nifty_dashboard.html"
