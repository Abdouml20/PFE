from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # Homepage - handles both authenticated and non-authenticated users
    path('', views.public_homepage, name='public_homepage'),
    path('feed/', views.feed, name='feed'),
    path('create-post/', views.create_post, name='create_post'),
    path('post/<uuid:pk>/', views.post_detail, name='post_detail'),
    
    # Social interactions
    path('post/<uuid:pk>/like/', views.like_post, name='like_post'),
    path('post/<uuid:pk>/save/', views.save_post, name='save_post'),
    path('post/<uuid:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    
    # Connections
    path('connections/', views.connections, name='connections'),
    path('send-connection/', views.send_connection_request, name='send_connection_request'),
    path('send-connection-ajax/', views.send_connection_request_ajax, name='send_connection_request_ajax'),
    path('cancel-connection-ajax/', views.cancel_connection_request, name='cancel_connection_request'),
    path('unfollow-artisan/', views.unfollow_artisan, name='unfollow_artisan'),
    path('connection-status/<int:user_id>/', views.get_connection_status, name='get_connection_status'),
    path('connection/<int:pk>/accept/', views.accept_connection, name='accept_connection'),
    path('connection/<int:pk>/reject/', views.reject_connection, name='reject_connection'),
    path('accept-connection-notification/<int:connection_id>/', views.accept_connection_from_notification, name='accept_connection_from_notification'),
    path('reject-connection-notification/<int:connection_id>/', views.reject_connection_from_notification, name='reject_connection_from_notification'),
    
    # Messaging
    path('messages/', views.messages_list, name='messages_list'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    
    # Notifications and discovery
    path('notifications/', views.notifications, name='notifications'),
    path('notification-counts/', views.get_notification_counts, name='get_notification_counts'),
    path('discover/', views.discover_users, name='discover_users'),
]
