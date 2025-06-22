from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Artist

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'availability', 'featured', 'created_at')
    list_filter = ('availability', 'featured')
    search_fields = ('name', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'bio')
        }),
        (_('Contact Information'), {
            'fields': ('website', 'phone', 'address')
        }),
        (_('Status'), {
            'fields': ('availability', 'featured')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
