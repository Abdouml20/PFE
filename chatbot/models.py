from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.

class ChatSession(models.Model):
    """Represents a chat session between a user and the bot"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_sessions')
    session_id = models.CharField(_('session id'), max_length=255, unique=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        verbose_name = _('chat session')
        verbose_name_plural = _('chat sessions')
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Chat session for {self.user.username}"
        return f"Chat session {self.session_id}"

class ChatMessage(models.Model):
    """Represents individual messages in a chat session"""
    MESSAGE_TYPES = (
        ('user', _('User')),
        ('bot', _('Bot')),
        ('system', _('System')),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(_('message type'), max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField(_('content'))
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    is_read = models.BooleanField(_('is read'), default=False)
    
    class Meta:
        verbose_name = _('chat message')
        verbose_name_plural = _('chat messages')
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class FAQ(models.Model):
    """Frequently Asked Questions for the chatbot"""
    question = models.CharField(_('question'), max_length=500)
    answer = models.TextField(_('answer'))
    keywords = models.TextField(_('keywords'), help_text=_('Comma-separated keywords for matching'))
    category = models.CharField(_('category'), max_length=100, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['category', 'question']
    
    def __str__(self):
        return self.question
    
    def get_keywords_list(self):
        """Return keywords as a list"""
        return [keyword.strip().lower() for keyword in self.keywords.split(',') if keyword.strip()]