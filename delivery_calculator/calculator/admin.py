from django.contrib import admin
from .models import DeliveryCalculation

@admin.register(DeliveryCalculation)
class DeliveryCalculationAdmin(admin.ModelAdmin):
    list_display = ['pickup_location', 'delivery_location', 'weight', 'total_price', 'created_at']
    list_filter = ['package_type', 'is_fragile', 'needs_insurance', 'created_at']
    search_fields = ['pickup_location', 'delivery_location']
    readonly_fields = ['distance', 'total_price', 'created_at']