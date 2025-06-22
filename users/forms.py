from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User
from allauth.account.forms import SignupForm

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm Password'), widget=forms.PasswordInput)
    delivery_agency = forms.CharField(label=_('Delivery Agency'), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter delivery agency name')}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'gender', 'wilaya', 'role', 'delivery_agency')
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'wilaya': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(_('Passwords do not match.'))
        return cd['password2']
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email already in use.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        delivery_agency = cleaned_data.get('delivery_agency')
        if role == 'artist' and not delivery_agency:
            self.add_error('delivery_agency', _('This field is required for artists.'))
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    delivery_agency = forms.CharField(label=_('Delivery Agency'), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter delivery agency name')}))
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'gender', 'wilaya', 'profile_picture', 'delivery_agency')
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'wilaya': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        role = getattr(self.instance, 'role', None)
        delivery_agency = cleaned_data.get('delivery_agency')
        if role == 'artist' and not delivery_agency:
            self.add_error('delivery_agency', _('This field is required for artists.'))
        return cleaned_data

class CustomSignupForm(SignupForm):
    ROLE_CHOICES = (
        ('artist', _('Artist')),
        ('customer', _('Customer')),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label=_('I want to join as'), widget=forms.Select(attrs={'class': 'form-select'}))
    delivery_agency = forms.CharField(label=_('Delivery Agency'), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter delivery agency name')}))

    def save(self, request):
        user = super().save(request)
        user.role = self.cleaned_data['role']
        user.delivery_agency = self.cleaned_data.get('delivery_agency', '')
        user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        delivery_agency = cleaned_data.get('delivery_agency')
        if role == 'artist' and not delivery_agency:
            self.add_error('delivery_agency', _('This field is required for artists.'))
        return cleaned_data
