#opc.py
import requests
import pandas as pd
from datetime import datetime
import pytz
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Headers & URLs ---
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en,gu;q=0.9,hi;q=0.8',
    'Referer': 'https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',
    'X-Requested-With': 'XMLHttpRequest'
}
URL_OC = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
URL_IDX = 'https://www.nseindia.com/api/allIndices'

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# ---------------------- Initialize NSE session ----------------------
def initialize_session():
    try:
        session.get('https://www.nseindia.com', headers=headers, timeout=10)
        session.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY', headers=headers, timeout=10)
    except Exception as e:
        print(f"⚠️ session init error: {e}")

# ---------------------- Fetch spot (safe) ----------------------
def get_spot_value():
    """Fetch the latest NIFTY 50 spot value safely."""
    try:
        res = session.get(URL_IDX, headers=headers, timeout=10)
        if res.status_code == 200:
            indices = res.json().get("data", [])
            for idx in indices:
                if idx.get("index") == "NIFTY 50":
                    return round(float(idx.get("last", 0)), 2)
    except Exception as e:
        print(f"⚠️ Spot fetch error: {e}")
    return 0.0

# ---------------------- Fetch option data ----------------------
def fetch_option_data(expiry=None):
    u = f"{URL_OC}&expiryDate={expiry}" if expiry else URL_OC
    try:
        res = session.get(u, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"API error: {e}")
        return None

# ---------------------- Main function ----------------------
def get_option_chain():
    initialize_session()
    opt_data = fetch_option_data()
    spot = get_spot_value()  # ✅ safe fallback

    if not opt_data or 'records' not in opt_data:
        print("❌ API failed to return valid data")
        return None, spot, pd.DataFrame()

    expiry_dates = opt_data['records'].get('expiryDates', [])
    underlying_value = opt_data['records'].get('underlyingValue', 0)
    spot_value = round(float(spot or underlying_value), 2)

    current_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    valid_expiries = [
        (e, datetime.strptime(e, '%d-%b-%Y').date()) for e in expiry_dates
        if datetime.strptime(e, '%d-%b-%Y').date() >= current_date
    ]
    current_expiry = valid_expiries[0][0] if valid_expiries else None

    # Filter & process option chain data
    raw_data = pd.DataFrame(opt_data['filtered']['data']).fillna(0)
    if raw_data.empty:
        return current_expiry, spot_value, pd.DataFrame()

    records = []
    for _, r in raw_data.iterrows():
        ce = r.get('CE', 0)
        pe = r.get('PE', 0)
        records.append({
            'Call IV': round(ce.get('impliedVolatility', 0), 2) if ce else 0,
            'Call OI': int(ce.get('openInterest', 0)) if ce else 0,
            'Call Chg OI': int(ce.get('changeinOpenInterest', 0)) if ce else 0,
            'Call LTP': round(ce.get('lastPrice', 0), 2) if ce else 0,
            'Strike Price': int(r['strikePrice']),
            'Put LTP': round(pe.get('lastPrice', 0), 2) if pe else 0,
            'Put Chg OI': int(pe.get('changeinOpenInterest', 0)) if pe else 0,
            'Put OI': int(pe.get('openInterest', 0)) if pe else 0,
            'Put IV': round(pe.get('impliedVolatility', 0), 2) if pe else 0,
        })

    df = pd.DataFrame(records)
    df['diff'] = abs(df['Strike Price'] - spot_value)
    atm = df.loc[df['diff'].idxmin(), 'Strike Price']

    df = pd.concat([
        df[df['Strike Price'] < atm].sort_values('Strike Price', ascending=False).head(10),
        df[df['Strike Price'] == atm],
        df[df['Strike Price'] > atm].sort_values('Strike Price').head(10)
    ]).sort_values('Strike Price', ascending=False).drop(columns=['diff'])

    return current_expiry, spot_value, df