from django.urls import path
#from django.conf.urls import url
from . import views

urlpatterns = [
    path('inventory', views.StockListView.as_view(), name='inventory'),
    path('s_new', views.StockCreateView.as_view(), name='new-stock'),
    path('stock/<pk>/edit', views.StockUpdateView.as_view(), name='edit-stock'),
    path('stock/<pk>/delete', views.StockDeleteView.as_view(), name='delete-stock'),
]
