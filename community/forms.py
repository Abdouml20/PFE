from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Post, PostImage, Comment, Message, Connection, Follow

User = get_user_model()

class PostForm(forms.ModelForm):
    """Form for creating and editing posts"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'post_type', 'tags', 'related_product', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('What are you working on?')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Share your story, techniques, or inspiration...')
            }),
            'post_type': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Add tags separated by commas (e.g., pottery, handmade, ceramics)')
            }),
            'related_product': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': _('Title'),
            'content': _('Content'),
            'post_type': _('Post Type'),
            'tags': _('Tags'),
            'related_product': _('Related Product (Optional)'),
            'is_public': _('Make this post public'),
        }

class PostImageForm(forms.ModelForm):
    """Form for adding images to posts"""
    class Meta:
        model = PostImage
        fields = ['image', 'caption', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Add a caption for this image')
            }),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'image': _('Image'),
            'caption': _('Caption'),
            'is_main': _('Main Image'),
        }

class CommentForm(forms.ModelForm):
    """Form for adding comments to posts"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Write a comment...')
            })
        }
        labels = {
            'content': _('Comment'),
        }

class MessageForm(forms.ModelForm):
    """Form for sending direct messages"""
    class Meta:
        model = Message
        fields = ['recipient', 'content']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Type your message...')
            })
        }
        labels = {
            'recipient': _('To'),
            'content': _('Message'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show users that the current user can message (connected users)
            connected_users = Connection.objects.filter(
                models.Q(from_user=user, status='accepted') | 
                models.Q(to_user=user, status='accepted')
            ).values_list('from_user', 'to_user')
            
            user_ids = set()
            for from_user, to_user in connected_users:
                user_ids.add(from_user)
                user_ids.add(to_user)
            
            # Remove current user from the list
            user_ids.discard(user.id)
            
            self.fields['recipient'].queryset = User.objects.filter(id__in=user_ids)

class ConnectionRequestForm(forms.ModelForm):
    """Form for sending connection requests"""
    class Meta:
        model = Connection
        fields = ['to_user']
        widgets = {
            'to_user': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'to_user': _('Connect with'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Exclude users already connected or pending
            connected_users = Connection.objects.filter(
                models.Q(from_user=user) | models.Q(to_user=user)
            ).values_list('from_user', 'to_user')
            
            user_ids = set()
            for from_user, to_user in connected_users:
                user_ids.add(from_user)
                user_ids.add(to_user)
            
            # Remove current user from the list
            user_ids.discard(user.id)
            
            self.fields['to_user'].queryset = User.objects.exclude(id__in=user_ids)
