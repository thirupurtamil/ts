from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path("selvi/", admin.site.urls),
    path('', include('ts.urls')),
    path('', include('ss.urls'))
    
    
]

