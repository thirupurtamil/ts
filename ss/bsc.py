# bsc/bsc.py
import math
import requests
import pandas as pd
from scipy.stats import norm
from datetime import datetime, date, time

def bs_price(S, K, T, r, sigma, option_type='call'):
    if sigma <= 0 or T <= 0:
        return max(S - K, 0.0) if option_type == 'call' else max(K - S, 0.0)
    d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    if option_type == 'call':
        return S*norm.cdf(d1) - K*math.exp(-r*T)*norm.cdf(d2)
    else:
        return K*math.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

def fetch_nifty_data():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    s = requests.Session()
    s.get("https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY", headers=headers, timeout=5)
    r = s.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

def bs_calculate(input_strike):
    data = fetch_nifty_data()
    records = data['records']
    spot = records['underlyingValue']
    expiry_date = records['expiryDates'][0]

    exp_date = datetime.strptime(expiry_date, "%d-%b-%Y").date()
    today = date.today()

    # ✅ Expiry day counting fix
    days_to_expiry = (exp_date - today).days + 1
    days_to_expiry = max(days_to_expiry, 0)

    T = days_to_expiry / 365
    r = 0.075

    atm_strike = round(spot / 50) * 50
    df = pd.DataFrame(records['data'])
    row = df[df['strikePrice'] == input_strike]
    if row.empty:
        return None, None

    row = row.iloc[0]
    ce, pe = row.get('CE', {}), row.get('PE', {})
    iv_call = (ce.get('impliedVolatility', 0)) / 100 
    iv_put = (pe.get('impliedVolatility', 0)) / 100
    mkt_call = ce.get('lastPrice', None)
    mkt_put = pe.get('lastPrice', None)

    spot_list = [atm_strike + (i * 50) for i in range(-6, 7)]
    results = []
    for s in spot_list:
        call_price = bs_price(s, input_strike, T, r, iv_call, 'call')
        put_price = bs_price(s, input_strike, T, r, iv_put, 'put')
        results.append({
            "Spot": s,
            "Call (BS)": round(call_price, 2),
            "Put (BS)": round(put_price, 2),
        })

    return {
        "spot": spot,
        "atm_strike": atm_strike,
        "expiry": expiry_date,
        "days": days_to_expiry,
        "mkt_call": mkt_call,
        "mkt_put": mkt_put,
        "iv_call": iv_call,
        "iv_put": iv_put
    }, results