from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Category

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'featured', 'created_at')
    list_filter = ('featured', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        (_('Hierarchy'), {
            'fields': ('parent',)
        }),
        (_('Status'), {
            'fields': ('featured',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
