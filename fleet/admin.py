from django.contrib import admin
from .models import CarBrand, Car


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'created_at')
    search_fields = ('name', 'country')
    ordering = ('name',)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'model_name', 'brand', 'year', 'daily_price',
        'capacity', 'status', 'pickup_address', 'created_at'
    )
    list_filter = ('status', 'brand', 'year', 'capacity')
    search_fields = ('model_name', 'brand__name', 'pickup_address', 'features')
    list_editable = ('status', 'daily_price')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
