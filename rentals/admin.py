from django.contrib import admin
from .models import RentalContract


@admin.register(RentalContract)
class RentalContractAdmin(admin.ModelAdmin):
    list_display = (
        'contract_code', 'customer', 'car', 'start_date',
        'end_date', 'total_price', 'status', 'created_at'
    )
    list_filter = ('status', 'start_date', 'end_date', 'created_at')
    search_fields = (
        'contract_code', 'customer__username', 'customer__first_name',
        'customer__last_name', 'customer__phone_number', 'car__model_name',
        'car__brand__name'
    )
    list_editable = ('status',)
    readonly_fields = ('contract_code', 'daily_rate_snapshot', 'total_price', 'created_at', 'updated_at')
    ordering = ('-created_at',)
