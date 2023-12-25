from . import views 
from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include,re_path

urlpatterns = [
    path('pis',views.pis,name='pis'),
    re_path(r'^product/', include(('pis_product.urls', 'product'),namespace='product'),),
    re_path(r'^retailer/', include(('pis_retailer.urls', 'retailer'), namespace='retailer')),
    re_path(r'^', include('pis_com.urls')),
    re_path(r'^sales/', include(('pis_sales.urls', 'sales'), namespace='sales')),
    
    
    
    
    re_path(r'^ledger/', include(('pis_ledger.urls','ledger'), namespace='ledger')),
    re_path(r'^expense/', include(('pis_expense.urls','expense'), namespace='expense')),
    re_path(r'^employee/', include(('pis_employees.urls','employee'), namespace='employee')),
    re_path(r'^supplier/', include(('pis_supplier.urls','supplier'), namespace='supplier')),
   
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
