from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderItem

# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ('price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email', 'status', 'paid', 'created_at')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'address', 'city', 'wilaya')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'paid')
        }),
        (_('Customer Information'), {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        (_('Shipping Information'), {
            'fields': ('address', 'wilaya', 'postal_code', 'city')
        }),
        (_('Additional Information'), {
            'fields': ('note',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'price', 'quantity')
    list_filter = ('order',)
    search_fields = ('product__name', 'order__id')
    raw_id_fields = ['product', 'order']
