from django.shortcuts import render
from django.shortcuts import render 
from django.http import HttpResponse
import datetime 
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





# Create your views here.



def home(request):
    return render (request,'papa/home.html',{})

def tss(request):
    msg = 'HAI'
    name = 'TAMIL'
    User = get_user_model()
    count= User.objects.count
    date = datetime.datetime.now()
    hour = int(date.strftime('%H'))
    if hour<12:
     msg+=  ',GOOD MORNING'
    else:
     msg+=  ',GOOD EVENING'
    
    date_dict = {'index_date':date ,'empname':name , 'greetings':msg, 'count':count , }
    return render (request,'papa/pa.html',context =date_dict)






