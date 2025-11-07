from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import Product, Picture

# Register your models here.
class PictureInline(admin.TabularInline):
    model = Picture
    extra = 1
    fields = ('image', 'description', 'is_main')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'category', 'artist', 'stock', 'available', 'featured', 'created_at')
    list_filter = ('available', 'featured', 'category', 'artist')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PictureInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Pricing'), {
            'fields': ('price', 'discount_price')
        }),
        (_('Categorization'), {
            'fields': ('category', 'artist')
        }),
        (_('Status'), {
            'fields': ('stock', 'available', 'featured')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'artist', 'image_thumbnail', 'is_main', 'created_at')
    list_filter = ('is_main', 'product', 'artist')
    search_fields = ('product__name', 'artist__name', 'description')
    readonly_fields = ('created_at', 'image_preview')
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_thumbnail.short_description = _('Thumbnail')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" />', obj.image.url)
        return "-"
    image_preview.short_description = _('Image preview')
