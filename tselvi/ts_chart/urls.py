from django.urls import path
from ts_chart import views

urlpatterns = [
    path('ichart/', views.ichart,name='ichart'),
    path('ichartdata/', views.ichartdata,name='ichartdata'),
    path('ichartview/', views.ichartview,name='ichartview'),
]
