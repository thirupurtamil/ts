from django.contrib import admin
from .models import NiftyExpiry, NiftyOptionSnapshot

@admin.register(NiftyExpiry)
class NiftyExpiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'expiry_date', 'created_at')
    ordering = ('-expiry_date',)

@admin.register(NiftyOptionSnapshot)
class NiftyOptionSnapshotAdmin(admin.ModelAdmin):
    list_display = ('expiry', 'fetch_date', 'sequence', 'option_type', 'strike', 'last_price', 'volume', 'open_interest')
    list_filter = ('fetch_date', 'expiry__expiry_date', 'option_type')
    search_fields = ('strike',)
    ordering = ('-fetch_date', 'sequence')
