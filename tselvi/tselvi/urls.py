from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include,re_path
from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('',include('accounts.urls')),
    path('',include('papa.urls')),
    path('',include('student.urls')),
    path('',include('mail.urls')),
    path('',include('ts_chart.urls')),
    path('',include('ts.urls')),
    path('',include('store.urls')),
    path('',include('ems.urls')),
    path('',include('homepage.urls')),
    path('',include('youtube.urls')),
    path('',include('inventory.urls')),
    path('',include('transactions.urls')),
    path('',include('dashboard.urls')),
    path('',include('otp.urls')),
    
]
if settings.DEBUG:
   urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
