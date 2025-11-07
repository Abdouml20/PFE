from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    image = models.ImageField(_('image'), upload_to='categories', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    featured = models.BooleanField(_('featured'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('categories:category_detail', kwargs={'slug': self.slug})
