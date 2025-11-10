from django.urls import path
from django.contrib import admin
from ss import views 
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    

    # 🏠 Home page
    path('', TemplateView.as_view(template_name='raj.html'), name='home'),
    path('nifty_data/', TemplateView.as_view(template_name='nifty_data.html'), name='nifty_datewise'),

    # 🔸 Nifty data datewise APIs
    path('api/nifty/datewise/', nifty_datewise_api, name='nifty_datewise_api'),
    path('api/nifty/delete/<date>/', delete_nifty_date_api, name='delete_nifty_date_api'),

    # 📊 Nifty 50 APIs
    path('api/nifty/', views.nifty_api, name='nifty_api'),
    path('api/nifty/weekly/', nifty_weekly_api, name='nifty_weekly_api'),
    path('nifty_weekly/', TemplateView.as_view(template_name='nifty_weekly.html'), name='nifty_weekly'),

    # 🧮 ACB pages
    path('acb/', TemplateView.as_view(template_name='acb.html'), name='acb_page'),
    path('api/acb/', views.acb_api, name='acb_api'),

    # ⚙️ Option Chain Frontend
    path('opc/', TemplateView.as_view(template_name='option_chain.html'), name='opc'),
    path('api/option_chain/', views.option_chain_api, name='option_chain_api'),

    # 🔹 LTP Similarity
    path('ltp/', TemplateView.as_view(template_name='ltp_similarity.html'), name='ltp'),
    path('api/ltp_similarity/', views.ltp_similarity_api, name='ltp_similarity_api'),

    # 🔹 Synthetic Future
    path('sf/', TemplateView.as_view(template_name='sf.html'), name='sf'),
    path('api/sf/', views.synthetic_future_api, name='synthetic_future_api'),

    # 🧮 BSC front-end page
    path('bsc/', TemplateView.as_view(template_name='bsc.html'), name='bsc'),
    path('api/bsc/', views.bsc_api, name='bsc_api'),
    path('api/bs/', views.bs_premium, name='bs_premium'),
    path('bs/', TemplateView.as_view(template_name='bs.html'), name='bs'),

    
]
