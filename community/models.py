from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
import uuid

# Create your models here.

class Post(models.Model):
    """Posts for showcasing artisan work - similar to LinkedIn posts"""
    POST_TYPE_CHOICES = (
        ('work', _('Work Showcase')),
        ('tip', _('Tip & Tutorial')),
        ('story', _('Story')),
        ('question', _('Question')),
        ('completed', _('Completed Work')),
        ('wip', _('Work in Progress')),
        ('inspiration', _('Inspiration')),
        ('tutorial', _('Tutorial')),
        ('announcement', _('Announcement')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    post_type = models.CharField(_('post type'), max_length=20, choices=POST_TYPE_CHOICES, default='completed')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='community_liked_posts', blank=True)
    saves = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='community_saved_posts', blank=True)
    is_featured = models.BooleanField(_('featured'), default=False)
    is_public = models.BooleanField(_('public'), default=True, help_text=_('Whether this post is visible to non-authenticated users'))
    tags = models.CharField(_('tags'), max_length=500, blank=True, help_text=_('Comma-separated tags'))
    
    # Link to product if this post is about a specific product
    related_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def get_absolute_url(self):
        return reverse('community:post_detail', kwargs={'pk': self.pk})
    
    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        return self.comments.count()
    
    def total_saves(self):
        return self.saves.count()
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

class PostImage(models.Model):
    """Images attached to posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('image'), upload_to='community/posts')
    caption = models.CharField(_('caption'), max_length=200, blank=True)
    is_main = models.BooleanField(_('main image'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('post image')
        verbose_name_plural = _('post images')
        ordering = ['-is_main', 'created_at']
    
    def __str__(self):
        return f"Image for {self.post.title}"

class Comment(models.Model):
    """Comments on posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='community_liked_comments', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    def total_likes(self):
        return self.likes.count()
    
    def total_replies(self):
        return self.replies.count()

class Connection(models.Model):
    """Connection system for artisans (mutual connections)"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('blocked', _('Blocked')),
    )
    
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_connections')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_connections')
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('connection')
        verbose_name_plural = _('connections')
        unique_together = ['from_user', 'to_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"

class Follow(models.Model):
    """Follow system for customers following artisans (one-way)"""
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('follow')
        verbose_name_plural = _('follows')
        unique_together = ['follower', 'following']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class Message(models.Model):
    """Direct messages between users"""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    is_read = models.BooleanField(_('is read'), default=False)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

class Conversation(models.Model):
    """Group messages into conversations"""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = [p.username for p in self.participants.all()]
        return f"Conversation: {', '.join(participant_names)}"

class Activity(models.Model):
    """Activity feed entries"""
    ACTIVITY_TYPE_CHOICES = (
        ('post_created', _('Created a post')),
        ('post_liked', _('Liked a post')),
        ('post_commented', _('Commented on a post')),
        ('product_added', _('Added a new product')),
        ('connection_made', _('Connected with someone')),
        ('profile_updated', _('Updated profile')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(_('activity type'), max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    # Optional references to related objects
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='targeted_activities')
    
    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.get_activity_type_display()}"

class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPE_CHOICES = (
        ('like', _('Someone liked your post')),
        ('comment', _('Someone commented on your post')),
        ('connection_request', _('New connection request')),
        ('connection_accepted', _('Connection request accepted')),
        ('connection_rejected', _('Connection request declined')),
        ('message', _('New message')),
        ('mention', _('You were mentioned')),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(_('notification type'), max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.CharField(_('message'), max_length=200)
    is_read = models.BooleanField(_('is read'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    # Optional references to related objects
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message_obj = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"
