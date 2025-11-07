from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from products.models import Product

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    )
    
    WILAYA_CHOICES = (
        ('adrar', _('Adrar')),
        ('chlef', _('Chlef')),
        ('laghouat', _('Laghouat')),
        ('oum-el-bouaghi', _('Oum El Bouaghi')),
        ('batna', _('Batna')),
        ('bejaia', _('Béjaïa')),
        ('biskra', _('Biskra')),
        ('bechar', _('Béchar')),
        ('blida', _('Blida')),
        ('bouira', _('Bouira')),
        ('tamanrasset', _('Tamanrasset')),
        ('tebessa', _('Tébessa')),
        ('tlemcen', _('Tlemcen')),
        ('tiaret', _('Tiaret')),
        ('tizi-ouzou', _('Tizi Ouzou')),
        ('algiers', _('Algiers')),
        ('djelfa', _('Djelfa')),
        ('jijel', _('Jijel')),
        ('setif', _('Sétif')),
        ('saida', _('Saïda')),
        ('skikda', _('Skikda')),
        ('sidi-bel-abbes', _('Sidi Bel Abbès')),
        ('annaba', _('Annaba')),
        ('guelma', _('Guelma')),
        ('constantine', _('Constantine')),
        ('medea', _('Médéa')),
        ('mostaganem', _('Mostaganem')),
        ('msila', _('M\'Sila')),
        ('mascara', _('Mascara')),
        ('ouargla', _('Ouargla')),
        ('oran', _('Oran')),
        ('el-bayadh', _('El Bayadh')),
        ('illizi', _('Illizi')),
        ('bordj-bou-arreridj', _('Bordj Bou Arréridj')),
        ('boumerdes', _('Boumerdès')),
        ('el-tarf', _('El Tarf')),
        ('tindouf', _('Tindouf')),
        ('tissemsilt', _('Tissemsilt')),
        ('el-oued', _('El Oued')),
        ('khenchela', _('Khenchela')),
        ('souk-ahras', _('Souk Ahras')),
        ('tipaza', _('Tipaza')),
        ('mila', _('Mila')),
        ('ain-defla', _('Aïn Defla')),
        ('naama', _('Naâma')),
        ('ain-temouchent', _('Aïn Témouchent')),
        ('ghardaia', _('Ghardaïa')),
        ('relizane', _('Relizane')),
        ('timimoun', _('Timimoun')),
        ('bordj-badji-mokhtar', _('Bordj Badji Mokhtar')),
        ('ouled-djellal', _('Ouled Djellal')),
        ('beni-abbes', _('Béni Abbès')),
        ('in-salah', _('In Salah')),
        ('in-guezzam', _('In Guezzam')),
        ('touggourt', _('Touggourt')),
        ('djanet', _('Djanet')),
        ('el-mghair', _('El M\'Ghair')),
        ('el-menia', _('El Menia')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=20)
    address = models.CharField(_('address'), max_length=250)
    wilaya = models.CharField(_('wilaya/region'), max_length=100, choices=WILAYA_CHOICES)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    city = models.CharField(_('city'), max_length=100)
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(_('note'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    paid = models.BooleanField(_('paid'), default=False)
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('orders:order_detail', kwargs={'pk': self.pk})

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name}'
    
    def get_cost(self):
        return self.price * self.quantity
