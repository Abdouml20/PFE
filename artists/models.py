from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Artist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artist_profile')
    name = models.CharField(_('artist name'), max_length=255)
    bio = models.TextField(_('biography'), blank=True)
    availability = models.BooleanField(_('available for commissions'), default=True)
    featured = models.BooleanField(_('featured artist'), default=False)
    website = models.URLField(_('website'), blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    address = models.TextField(_('address'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('artist')
        verbose_name_plural = _('artists')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('artists:artist_detail', kwargs={'pk': self.pk})
