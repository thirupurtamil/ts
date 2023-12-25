from nsetools import *
from nsepython import * 
from jugaad_data.nse import *
from pprint import pprint
import webbrowser
from time import sleep
from nsetools import *
from nsepython import * 
from jugaad_data.nse import *
from pprint import pprint
import webbrowser
from time import sleep
import requests
import pandas as pd
import time
import json
from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests
import pandas as pd
import time
from datetime import *
from time import *


import requests
import pandas as pd
import time
nse_obj = Nse()  
n = NSELive()     
nse = Nse()
nifty_data = n.live_index('NIFTY 50')


now = datetime.now() 
current_time = now.strftime("%H:%M:%S") 
nifty_data = n.live_index('NIFTY 50')
def p_time(time): 
    return time.strftime('%I:%M %p') 
time = datetime.now() 
time_format = p_time(time) 



#print("NSE Object:", nse_obj)
#print(indices)
#print("Name:",nifty_data['name'],)
#print("Time:", nifty_data['timestamp'],) 
#print("Last price:",nifty_data['data'][0]['lastPrice'],)
#print("Open price:",nifty_data['data'][0]['open'],)
#print("Daylow.   :",nifty_data['data'][0]['dayLow'],)
#print("Dayhigh.  :",nifty_data['data'][0]['dayHigh'],)
#print("Time:",time_format)
#print("Name:",nifty_data['name'],)
#print("NIFTY 50:",nifty_data['data'][0]['lastPrice'],)
#print("SERVER:", nifty_data['timestamp'],) 








url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37','accept-encoding': 'gzip, deflate, br','accept-language': 'en-GB,en;q=0.9,en-US;q=0.8'}

session = requests.Session()
request = session.get(url,headers=headers)
cookies = dict(request.cookies)









data=[]


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',}
with requests.session() as req:
    req.get('https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY',headers = headers)

    api_req=req.get('https://www.nseindia.com/api/quote-derivative?symbol=NIFTY',headers = headers).json()
    for item in api_req['stocks']:
        data.append([
            item['metadata']['strikePrice'],
            item['metadata']['optionType'],
            item['metadata']['openPrice'],
            item['metadata']["highPrice"],
            item['metadata']['lowPrice'],
            item['metadata']['lastPrice'],])
            
           

cols=['STRIKEPRICE','OPTION','OPEN',"HIGH",'LOW','LAST']

df = pd.DataFrame(data, columns=cols)

get_rows = df.head(14)

#print (get_rows)

    


