import requests
import pandas as pd
from datetime import datetime

data = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
}

with requests.Session() as req:
    # Initial request to get cookies
    req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY', headers=headers)
    
    # Capture fetch time
    fetch_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    api_req = req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY', headers=headers).json()
    
    for item in api_req['stocks']:
        data.append([
            item['metadata']['strikePrice'],
            item['metadata']['optionType'],
            item['metadata']['openPrice'],
            item['metadata']["highPrice"],
            item['metadata']["lastPrice"],
            item['metadata']["lowPrice"],
            item['metadata']['numberOfContractsTraded'],
            item['metadata']['totalTurnover'],
            item['marketDeptOrderBook']['otherInfo']['impliedVolatility']
        ])

df = pd.DataFrame(data, columns=[
    'Strike', 'Option', 'open', 'high', 'ltp', 'low',
    'volume', 'value', 'iv'
])

# 💥 Print fetch time on top of the table
print(f"\n🕒 Server Fetch Time: {fetch_time}\n")
print(df.head(7).to_string(index=False))
