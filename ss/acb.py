import requests
import pandas as pd

def get_acb_data():
    data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 ...',
    }

    try:
        with requests.Session() as req:
            # NSE cookie initialization
            req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY', headers=headers)
            api_req = req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY', headers=headers).json()

            stocks = api_req.get('stocks', [])
            if not stocks:
                # ❌ Response not allowed here
                # ✅ Instead, just return empty DataFrame
                return pd.DataFrame()

            for item in stocks:
                meta = item.get('metadata', {})
                trade = item.get('marketDeptOrderBook', {}).get('tradeInfo', {})
                other = item.get('marketDeptOrderBook', {}).get('otherInfo', {})

                data.append({
                    'Strike': meta.get('strikePrice'),
                    'Option': meta.get('optionType'),
                    'Open': meta.get('openPrice'),
                    'High': meta.get('highPrice'),
                    'LTP': meta.get('lastPrice'),
                    'Low': meta.get('lowPrice'),
                    'Close': meta.get('closePrice'),
                    'Volume': meta.get('numberOfContractsTraded'),
                    'Value': meta.get('totalTurnover'),
                    'OpenInterest': trade.get('openInterest'),
                    'IV': other.get('impliedVolatility')
                })

        # 🔹 First 14 rows only
        df = pd.DataFrame(data).head(14)
        return df

    except Exception as e:
        print(f"⚠️ Error fetching ACB data: {e}")
        return pd.DataFrame()