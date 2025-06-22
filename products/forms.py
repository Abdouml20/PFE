from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import inlineformset_factory

from .models import Product, Picture
from categories.models import Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'discount_price', 'craft_category', 'stock', 'available', 'video')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Must be less than original price')}),
            'craft_category': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')
        
        if discount_price is not None and price is not None:
            if discount_price >= price:
                self.add_error('discount_price', _('Discount price must be less than the original price.'))
                
        return cleaned_data

class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ('image', 'description', 'is_main')
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Create a formset for product pictures
PictureFormSet = inlineformset_factory(
    Product, 
    Picture, 
    form=PictureForm,
    extra=3,
    can_delete=True,
    max_num=5,
)
