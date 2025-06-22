from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from categories.models import Category
from artists.models import Artist
import os

# Create your models here.
class Product(models.Model):
    CRAFT_CHOICES = (
        ('traditional', _('Traditional')),
        ('clothing', _('Clothing')),
        ('accessories', _('Accessories')),
        ('jewelry', _('Jewelry')),
        ('home-decor', _('Home Decor')),
        ('crockery', _('Crockery')),
        ('toys-games', _('Toys & Games')),
        ('art-painting', _('Art & Painting')),
        ('gift-ideas', _('Gift Ideas')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    description = models.TextField(_('description'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(_('discount price'), max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='products')
    craft_category = models.CharField(_('craft category'), max_length=20, choices=CRAFT_CHOICES, blank=True)
    stock = models.PositiveIntegerField(_('stock'), default=1)
    available = models.BooleanField(_('available'), default=True)
    featured = models.BooleanField(_('featured'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    video = models.FileField(_('video'), upload_to='product_videos', blank=True, null=True)
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def video_type(self):
        if self.video and self.video.name:
            name, extension = os.path.splitext(self.video.name)
            return f'video/{extension.lower().replace(".", "")}'
        return ''
    
    @property
    def get_discount_percentage(self):
        if self.discount_price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return int(discount)
        return 0
    
    @property
    def main_image(self):
        return self.images.first()

class Picture(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('image'), upload_to='products')
    description = models.CharField(_('description'), max_length=255, blank=True)
    is_main = models.BooleanField(_('main image'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('picture')
        verbose_name_plural = _('pictures')
        ordering = ['-is_main', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
