from django.shortcuts import render
from django.shortcuts import render 
from django.http import HttpResponse
import datetime 
#from datetime import datetime
import platform 
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy


from nsetools import Nse
from nsepy import get_history
from jugaad_data.nse import NSELive
from IPython.display import HTML
import webbrowser
from time import sleep
import requests
import pandas as pd
import time
import json
from bs4 import BeautifulSoup as bs

import requests
import pandas as pd










def home(request):
    return render (request,'home.html')



def oh(request): 
   template = loader.get_template('myfirst.html')                
   return HttpResponse(template.render())



def members(request):
  mymembers = Member.objects.all().values()
  template = loader.get_template('all_members.html')
  context = {
    'mymembers': mymembers,
  }
  return HttpResponse(template.render(context, request))



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

df = pd.DataFrame(data,columns=cols)
 


get_rows = df.head(14)



def home(request):
    return render (request,'home.html',{})

def tss(request):
    msg = 'HAI'
    name = 'TAMIL'
    User = get_user_model()
    count= User.objects.count
    nse_obj = Nse()  
    n = NSELive()     
    nse = Nse()
    nifty_data = n.live_index('NIFTY 50')
    

    op=("Open price:",nifty_data['data'][0]['open'],)

  
    

   
   
   
   

    date = datetime.datetime.now()
    hour = int(date.strftime('%H'))
    if hour<12:
     msg+=  ',GOOD MORNING'
    else:
     msg+=  ',GOOD EVENING'
     
    date_dict = {'index_date':date ,'empname':name , 'greetings':msg,'nifty_data':op,'get_rows':get_rows, 'count':count ,'nse_obj':nse_obj, }
    return render (request,'papa.html',context =date_dict)










