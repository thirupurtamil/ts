from django.urls import path
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
from django.urls import path
from django.contrib import admin


from homepage import views





urlpatterns=[
    path('inv', views.HomeView.as_view(), name='inv'),
    path('about',views.AboutView.as_view(),name ='about'),
    
]












