from django.contrib import admin 
from django.urls import include, path 
from oh import views



urlpatterns = [ 
   
      path('', include('oh.urls')),              
      path('admin/', admin.site.urls), ]
