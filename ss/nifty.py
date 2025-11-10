# Nifty.py
import requests
import pandas as pd
from datetime import datetime

def get_nifty_ohlc():
    """Fetch NIFTY 50 OHLC data with all fields & calculations"""

    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", [])
    except Exception as e:
        print("❌ NSE fetch error:", e)
        return {}

    df = pd.DataFrame(data)
    if df.empty or "symbol" not in df.columns:
        print("⚠️ NSE API structure unexpected.")
        return {}

    nifty = df[df["symbol"] == "NIFTY 50"]
    if nifty.empty:
        print("⚠️ NIFTY 50 not found in API data.")
        return {}

    row = nifty.iloc[0]

    # Safe values
    prev_close = float(row.get("previousClose", 0))
    open_ = float(row.get("open", 0))
    day_high = float(row.get("dayHigh", 0))
    day_low = float(row.get("dayLow", 0))
    last_price = float(row.get("lastPrice", 0))

    # Calculations
    High = round(day_high - open_, 2)
    Low = round(open_ - day_low, 2)
    Range = round(day_high - day_low, 2)
    Gap = round(open_ - prev_close, 2)
    Change = round(last_price - prev_close, 2)

    return {
        "previousClose": round(prev_close, 2),
        "open": round(open_, 2),
        "dayHigh": round(day_high, 2),
        "dayLow": round(day_low, 2),
        "lastPrice": round(last_price, 2),
        "High": High,
        "Low": Low,
        "Range": Range,
        "Gap": Gap,
        "Change": Change,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
