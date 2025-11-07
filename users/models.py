from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    )
    
    ROLE_CHOICES = (
        ('artist', _('Artist')),
        ('customer', _('Customer')),
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
    
    email = models.EmailField(_('email address'), unique=True)
    gender = models.CharField(_('gender'), max_length=1, choices=GENDER_CHOICES, blank=True)
    wilaya = models.CharField(_('region'), max_length=100, choices=WILAYA_CHOICES, blank=True)
    role = models.CharField(_('role'), max_length=10, choices=ROLE_CHOICES, default='customer')
    profile_picture = models.ImageField(_('profile picture'), upload_to='profile_pics', blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    delivery_agency = models.CharField(_('delivery agency'), max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.username
