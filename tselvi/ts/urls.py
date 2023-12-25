from django.contrib import admin
from django.urls import path,include 
from ts import views 

urlpatterns = [
    path ('bt',views.bt,name='bt'),
    path ('bt1',views.bt1,name='bt1'),
    path('category/', views.CategoryList.as_view(), name='category_list'),
    path('products/', views.ProductList.as_view(), name='product_list'),


    
    
]
