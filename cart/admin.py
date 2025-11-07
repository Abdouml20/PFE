from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Cart, CartItem

# Register your models here.
class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'get_total_items', 'get_total_cost', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'session_id')
    readonly_fields = ('created_at', 'updated_at', 'get_total_cost', 'get_total_items')
    inlines = [CartItemInline]
    fieldsets = (
        (None, {
            'fields': ('user', 'session_id')
        }),
        (_('Cart Summary'), {
            'fields': ('get_total_items', 'get_total_cost')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = _('Total Items')
    
    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = _('Total Cost')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'get_cost', 'created_at')
    list_filter = ('cart', 'created_at')
    search_fields = ('product__name', 'cart__user__username')
    raw_id_fields = ['product', 'cart']
    readonly_fields = ('created_at', 'updated_at', 'get_cost')
    
    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = _('Cost')
