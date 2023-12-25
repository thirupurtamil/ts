from django.urls import path
from . import views













urlpatterns = [
    path('', views.home, name='home'),
    path('oh/', views.oh, name='oh'),
    path ('tss',views.tss,name='tss'),
]