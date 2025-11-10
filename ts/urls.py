from django.urls import path
from django.contrib import admin
from ts.views import *
from django.views.generic import TemplateView

urlpatterns = [
    
    # 🔥 Nifty Option Data Fetch + Dashboard
    path('fetch-nifty/', NiftyFetchView.as_view(), name='fetch_nifty'),
    path('nifty-by-fetch-date/', NiftyByFetchDateView.as_view(), name='nifty-by-fetch-date'),
    path('cleanup-expired/', ExpiryCleanupView.as_view(), name='cleanup-expired'),
    path('dashboard/', NiftyDashboardView.as_view(), name='nifty_dashboard'),

    # ✅ FIXED — added "nifty/api/" prefix for frontend compatibility
    path('nifty/api/expiries/', ExpiryListAPI.as_view(), name='api-expiries'),
    path('nifty/api/fetch-dates/<str:expiry_date>/', FetchDateListAPI.as_view(), name='api-fetch-dates'),
    path('nifty/api/nifty-data/', NiftyDataAPI.as_view(), name='api-nifty-data'),
]
