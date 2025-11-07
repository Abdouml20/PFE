from django.contrib.auth import get_user_model

User = get_user_model()

def notification_counts(request):
    """Add notification and message counts to all templates"""
    if request.user.is_authenticated:
        # Get unread notifications count
        unread_notifications = request.user.notifications.filter(is_read=False).count()
        
        # Get unread messages count (messages where user is recipient and not read)
        unread_messages = request.user.received_messages.filter(is_read=False).count()
        
        return {
            'unread_notifications_count': unread_notifications,
            'unread_messages_count': unread_messages,
        }
    return {
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
    }
