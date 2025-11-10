from datetime import datetime, date
import pandas as pd
import requests

from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Max, Min

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import NiftyData
from .opc import get_option_chain
from .bs import black_scholes
from .bsc import bs_calculate
from .nifty import get_nifty_ohlc
from .acb import get_acb_data





@api_view(['GET'])
def nifty_api(request):
    """
    Fetch NIFTY 50 OHLC data from NSE, save to DB, and return latest values.
    """
    try:
        # ✅ Fetch fresh data
        data = get_nifty_ohlc()
        if not data:
            latest = NiftyData.objects.order_by('-date').first()
            if latest:
                return Response({
                    "message": "⚠️ Live data not available. Showing last saved record.",
                    **{f.name: getattr(latest, f.name) for f in NiftyData._meta.fields}
                })
            return Response({"error": "⚠️ NIFTY Data கிடைக்கவில்லை"}, status=500)

        # ✅ Timestamp convert to timezone-aware
        ts = pd.to_datetime(data.get("Timestamp"), errors="coerce")
        if isinstance(ts, datetime) and timezone.is_naive(ts):
            ts = timezone.make_aware(ts)

        # ✅ Save or update today's record
        NiftyData.objects.update_or_create(
            date=datetime.now().date(),
            defaults={**data, "Timestamp": ts}
        )

        # ✅ Return JSON to frontend
        return Response(data)

    except Exception as e:
        return Response({"error": f"❌ Server Error: {e}"}, status=500)






@api_view(['GET'])
def nifty_datewise_api(request):
    """📆 Return all NIFTY 50 date-wise data as JSON"""
    # Optional refresh
    if request.GET.get("refresh"):
        data = get_nifty_ohlc()
        if data:
            ts = pd.to_datetime(data.get("Timestamp"), errors="coerce")
            if isinstance(ts, datetime) and timezone.is_naive(ts):
                ts = timezone.make_aware(ts)
            NiftyData.objects.update_or_create(
                date=datetime.now().date(),
                defaults={**data, "Timestamp": ts}
            )

    # Fetch all data
    data_list = NiftyData.objects.all().values()
    return Response(list(data_list))


@api_view(['DELETE'])
def delete_nifty_date_api(request, date):
    """🗑 Delete a single date record"""
    try:
        obj = NiftyData.objects.get(date=date)
        obj.delete()
        return Response({"message": f"✅ {date} நாளின் தரவு நீக்கப்பட்டது"})
    except NiftyData.DoesNotExist:
        return Response({"error": f"⚠️ {date} தேதிக்கு தரவு இல்லை"}, status=404)


@api_view(['GET'])
def acb_api(request):
    df = get_acb_data()
    if df.empty:
        return Response({"error": "⚠️ ACB தரவு கிடைக்கவில்லை."}, status=500)

    # --- Range Logic ---
    first6 = df.head(6)
    call_rows = first6[first6["Option"].str.upper() == "CALL"]
    put_rows = first6[first6["Option"].str.upper() == "PUT"]

    rangeUp = call_rows["Strike"].max() if not call_rows.empty else 0
    rangeDown = put_rows["Strike"].min() if not put_rows.empty else 0
    rangeVal = rangeUp - rangeDown

    # --- High Value Strike ---
    grouped = df.groupby("Strike").agg({"Value": "sum"}).reset_index()
    max_row = grouped.loc[grouped["Value"].idxmax()]
    max_strike, max_value = int(max_row["Strike"]), max_row["Value"]

    # --- Near Strike Logic ---
    def get_near(df, strike, opt_type):
        filt = df[df["Option"].str.upper().isin([opt_type, opt_type[:2]])]
        if filt.empty:
            return {}
        exact = filt[filt["Strike"] == strike]
        if not exact.empty:
            return exact.iloc[0].to_dict()
        near = filt.iloc[(filt["Strike"] - strike).abs().idxmin()]
        return near.to_dict()

    call_row = get_near(df, max_strike, "CALL")
    put_row = get_near(df, max_strike, "PUT")

    # --- Prepare Response ---
    result = {
        "records": len(df),
        "max_strike": max_strike,
        "max_total_value": max_value,
        "call_ltp": call_row.get("LTP", 0),
        "put_ltp": put_row.get("LTP", 0),
        "rangeUp": rangeUp,
        "rangeDown": rangeDown,
        "range": rangeVal,
        "data": df.to_dict(orient='records')
    }

    return Response(result)




@api_view(['GET'])
def nifty_weekly_api(request):
    """DB-லிருந்து வாரந்தோறும் (Mon–Fri) NIFTY High, Low, Range எடுத்து காட்டும் API"""

    data = NiftyData.objects.all().order_by('date')

    if not data.exists():
        return Response({"error": "⚠️ Data not found"}, status=404)

    weekly_data = {}

    # 🔹 ஒவ்வொரு நாளின் data-வையும் வார வாரமா பிரிக்கிறோம்
    for row in data:
        year, week_num, _ = row.date.isocalendar()
        key = f"{year}-W{week_num}"

        if key not in weekly_data:
            weekly_data[key] = {
                "start_date": row.date,
                "end_date": row.date,
                "high": row.dayHigh or 0,
                "low": row.dayLow or 0,
            }
        else:
            weekly_data[key]["high"] = max(weekly_data[key]["high"], row.dayHigh or 0)
            weekly_data[key]["low"] = min(weekly_data[key]["low"], row.dayLow or 0)
            weekly_data[key]["end_date"] = row.date

    # 🔹 Range calculation
    result = []
    for key, val in weekly_data.items():
        week_high = val["high"]
        week_low = val["low"]
        result.append({
            "week": key,
            "start_date": val["start_date"],
            "end_date": val["end_date"],
            "weekly_high": round(week_high, 2),
            "weekly_low": round(week_low, 2),
            "weekly_range": round(week_high - week_low, 2),
        })

    # 🔹 புதிய data-விலிருந்து வரிசை மாற்றம் (புதியது முதல்)
    result.sort(key=lambda x: x["start_date"], reverse=True)

    return Response(result)
























@api_view(['GET'])
def option_chain_api(request):
    expiry, spot, df = get_option_chain()

    if df.empty:
        return Response({"message": "⚠️ Data கிடைக்கவில்லை."}, status=404)

    # Calculate max/min strikes
    call_max_strike = int(df.loc[df['Call Chg OI'].idxmax(), 'Strike Price'])
    put_max_strike = int(df.loc[df['Put Chg OI'].idxmax(), 'Strike Price'])
    call_min_strike = int(df.loc[df['Call Chg OI'].idxmin(), 'Strike Price'])
    put_min_strike = int(df.loc[df['Put Chg OI'].idxmin(), 'Strike Price'])

    # Convert table to JSON
    table_json = df.to_dict(orient='records')

    data = {
        "expiry": expiry,
        "spot": spot,
        "call_max_strike": call_max_strike,
        "put_max_strike": put_max_strike,
        "call_min_strike": call_min_strike,
        "put_min_strike": put_min_strike,
        "option_chain": table_json,
    }

    return Response(data)








# ---------- LTP Similarity ----------
def check_ltp_similarity(filtered_df):
    if filtered_df.empty:
        return {"message": "⚠️ Option data காலியாக உள்ளது.", "matches": [], "closest": {}}

    matches = []
    for _, row in filtered_df.iterrows():
        call, put, strike = row['Call LTP'], row['Put LTP'], row['Strike Price']
        diff = abs(call - put)
        if diff <= 1:
            matches.append({
                "Strike": int(strike),
                "Call": round(call, 2),
                "Put": round(put, 2),
                "Total": round(call + put, 2),
                "Diff": round(diff, 2)
            })

    if matches:
        return {"matches": matches, "closest": {}}

    filtered_df["Diff"] = abs(filtered_df["Call LTP"] - filtered_df["Put LTP"])
    row = filtered_df.loc[filtered_df["Diff"].idxmin()]
    strike, call, put, diff = int(row["Strike Price"]), row["Call LTP"], row["Put LTP"], row["Diff"]
    total = round(call + put, 2)

    return {
        "matches": [],
        "closest": {
            "Strike": strike,
            "Call": round(call, 2),
            "Put": round(put, 2),
            "Total": total,
            "Diff": round(diff, 2),
            "Added_Premium": round(total / 2, 2),
            "R1": int(strike + call),
            "R2": int(strike + total),
            "S1": int(strike - call),
            "S2": int(strike - total),
        },
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def ltp_similarity_api(request):
    expiry, spot, df = get_option_chain()
    if df.empty:
        return Response({"message": "⚠️ NSE Data கிடைக்கவில்லை."}, status=404)

    result = check_ltp_similarity(df)
    result.update({
        "spot": spot,
        "expiry": expiry
    })

    return Response(result)






def synthetic_future_api(request):
    expiry, spot, df = get_option_chain()
    if df.empty:
        return JsonResponse({"message": "⚠️ NSE Data கிடைக்கவில்லை."})

    # 🔹 Calculate Difference & Closest
    df["Diff"] = abs(df["Call LTP"] - df["Put LTP"])
    closest = df.loc[df["Diff"].idxmin()]

    call_ltp = round(closest["Call LTP"], 2)
    put_ltp = round(closest["Put LTP"], 2)
    strike = int(closest["Strike Price"])
    diff = round(call_ltp - put_ltp, 2)
    total = round(call_ltp + put_ltp, 2)
    sf_value = round(strike + diff, 2) if diff >= 0 else round(strike - abs(diff), 2)

    # 🔹 Compute Synthetic Future for all strikes
    df["Synthetic_Future"] = df.apply(
        lambda r: round(r["Strike Price"] + (r["Call LTP"] - r["Put LTP"]), 2)
        if (r["Call LTP"] - r["Put LTP"]) >= 0
        else round(r["Strike Price"] - abs(r["Call LTP"] - r["Put LTP"]), 2),
        axis=1,
    )

    synthetic_list = [
        {
            "Strike": int(r["Strike Price"]),
            "Call": round(r["Call LTP"], 2),
            "Put": round(r["Put LTP"], 2),
            "Diff": round(r["Call LTP"] - r["Put LTP"], 2),
            "Synthetic_Future": r["Synthetic_Future"]
        }
        for _, r in df.iterrows()
    ]

    # 🔹 Prepare JSON Response
    result = {
        "spot": spot,
        "expiry": expiry,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "closest": {
            "Strike": strike,
            "Call": call_ltp,
            "Put": put_ltp,
            "Total": total,
            "Diff": abs(diff),
            "Added_Premium": round(total / 2, 2),
            "Synthetic_Future": sf_value,
            "R1": int(strike + call_ltp),
            "R2": int(strike + total),
            "S1": int(strike - call_ltp),
            "S2": int(strike - total),
            "res1": int(sf_value + call_ltp),
            "res2": int(sf_value + total),
            "sup1": int(sf_value - call_ltp),
            "sup2": int(sf_value - total),
        },
        "synthetic": synthetic_list,
    }

    return JsonResponse(result, safe=False)




def bsc_api(request):
    strike = request.GET.get("strike")
    if not strike:
        return JsonResponse({"error": "❌ Please provide ?strike=xxxx"}, status=400)
    try:
        strike = int(strike)
        info, results = bs_calculate(strike)
        if info is None:
            return JsonResponse({"error": "⚠️ Invalid strike or data not found"}, status=404)
        return JsonResponse({
            "status": "ok",
            "info": info,
            "data": results
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






@api_view(['GET'])
def bs_premium(request):
    try:
        S = float(request.GET.get('spot', 0))
        K = float(request.GET.get('strike', 0))
        days = int(request.GET.get('days', 0))
        iv = float(request.GET.get('iv', 0))
        r = float(request.GET.get('r', 0))
        option_type = request.GET.get('type', 'call').lower()

        # adjust %
        if iv > 1: iv /= 100
        if r > 1: r /= 100

        T = days / 365
        premium = black_scholes(S, K, T, r, iv, option_type)

        return Response({
            "spot": S,
            "strike": K,
            "days": days,
            "iv": iv,
            "r": r,
            "type": option_type,
            "premium": round(premium, 2)
        })

    except Exception as e:
        return Response({"error": str(e)})











