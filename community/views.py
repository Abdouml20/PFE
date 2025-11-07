from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Post, PostImage, Comment, Connection, Message, Conversation, Activity, Notification, Follow
from .forms import PostForm, PostImageForm, CommentForm, MessageForm, ConnectionRequestForm
from products.models import Product

User = get_user_model()

def feed(request):
    """Main community homepage showing posts and featured artisans"""
    # Get all posts from all users (public community feed)
    posts = Post.objects.all().select_related('author').prefetch_related('images', 'likes', 'comments').order_by('-created_at')
    
    # Add pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get featured artisans (artists with most posts or connections)
    from artists.models import Artist
    featured_artisans = Artist.objects.select_related('user').annotate(
        post_count=Count('user__posts')
    ).order_by('-post_count')[:6]
    
    # Get some stats for the sidebar
    total_posts = Post.objects.count()
    total_users = User.objects.filter(role='artist').count()
    
    # Get recent activities
    recent_activities = Activity.objects.select_related('user', 'post').order_by('-created_at')[:5]
    
    context = {
        'posts': posts,
        'featured_artisans': featured_artisans,
        'recent_activities': recent_activities,
        'title': _('Community Feed'),
        'total_posts': total_posts,
        'total_users': total_users,
    }
    return render(request, 'community/homepage.html', context)

def public_homepage(request):
    """Public homepage for non-authenticated users"""
    # If user is authenticated, redirect to their feed
    if request.user.is_authenticated:
        return redirect('community:feed')
    
    # Get featured posts (public posts)
    posts = Post.objects.filter(is_public=True).select_related('author').prefetch_related('images', 'likes', 'comments').order_by('-created_at')[:6]
    
    # Get featured artisans
    from artists.models import Artist
    featured_artisans = Artist.objects.select_related('user').annotate(
        post_count=Count('user__posts')
    ).order_by('-post_count')[:8]
    
    # Get some stats
    total_posts = Post.objects.filter(is_public=True).count()
    total_users = User.objects.filter(role='artist').count()
    
    context = {
        'posts': posts,
        'featured_artisans': featured_artisans,
        'title': _('Welcome to Crafty Community'),
        'total_posts': total_posts,
        'total_users': total_users,
    }
    return render(request, 'community/public_homepage.html', context)

@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            
            # If product is selected, copy product images first
            if post.related_product:
                from products.models import Picture
                from django.core.files.base import ContentFile
                from django.core.files.storage import default_storage
                import os
                import time
                import logging
                
                logger = logging.getLogger(__name__)
                product_images = Picture.objects.filter(product=post.related_product).order_by('-is_main', 'created_at')
                images_copied = 0
                
                if not product_images.exists():
                    messages.warning(request, _('The selected product has no images to copy.'))
                else:
                    for i, product_image in enumerate(product_images):
                        try:
                            # Try to copy the image file using Django's file field
                            if product_image.image and product_image.image.name:
                                # Method 1: Try using the file field directly
                                try:
                                    # Open the source image
                                    source_file = product_image.image
                                    source_file.open('rb')
                                    file_content = source_file.read()
                                    source_file.seek(0)  # Reset file pointer
                                    
                                    # Generate a unique filename
                                    original_name = os.path.basename(product_image.image.name)
                                    name, ext = os.path.splitext(original_name)
                                    unique_name = f"community/posts/product_{post.id}_{int(time.time())}_{i}{ext}"
                                    
                                    # Create ContentFile with the content
                                    image_file = ContentFile(file_content)
                                    image_file.name = unique_name
                                    
                                    # Create PostImage with the file
                                    post_image = PostImage(
                                        post=post,
                                        image=image_file,
                                        is_main=(i == 0)
                                    )
                                    post_image.save()  # Save explicitly to ensure file is written
                                    source_file.close()
                                    
                                    images_copied += 1
                                    logger.info(f"Successfully copied product image {product_image.id} to post {post.id}")
                                    
                                except Exception as e1:
                                    logger.error(f"Method 1 failed for image {product_image.id}: {str(e1)}")
                                    # Method 2: Try using file path
                                    try:
                                        if hasattr(product_image.image, 'path'):
                                            image_path = product_image.image.path
                                            if os.path.exists(image_path):
                                                # Read file from disk
                                                with open(image_path, 'rb') as f:
                                                    file_content = f.read()
                                                
                                                # Generate unique filename
                                                original_name = os.path.basename(product_image.image.name)
                                                name, ext = os.path.splitext(original_name)
                                                unique_name = f"community/posts/product_{post.id}_{int(time.time())}_{i}{ext}"
                                                
                                                # Create ContentFile
                                                image_file = ContentFile(file_content)
                                                image_file.name = unique_name
                                                
                                                # Create PostImage
                                                post_image = PostImage(
                                                    post=post,
                                                    image=image_file,
                                                    is_main=(i == 0)
                                                )
                                                post_image.save()  # Save explicitly
                                                images_copied += 1
                                                logger.info(f"Successfully copied product image {product_image.id} using method 2")
                                            else:
                                                logger.error(f"Image path does not exist: {image_path}")
                                        else:
                                            logger.error(f"Product image {product_image.id} has no path attribute")
                                    except Exception as e2:
                                        logger.error(f"Method 2 also failed for image {product_image.id}: {str(e2)}")
                                        
                        except Exception as e:
                            logger.error(f"Error copying product image {product_image.id}: {str(e)}")
                            continue
                    
                    if images_copied > 0:
                        messages.info(request, _('{count} product image(s) have been added to your post.').format(count=images_copied))
                    else:
                        messages.warning(request, _('Could not copy product images. Please try uploading them manually.'))
                        logger.warning(f"Failed to copy any images for product {post.related_product.id} to post {post.id}")
            
            # Handle additional image uploads from form (these will be added after product images)
            images = request.FILES.getlist('images')
            for image in images:
                PostImage.objects.create(
                    post=post,
                    image=image,
                    is_main=False  # Don't make uploaded images main since product images are already there
                )
            
            # Create activity
            Activity.objects.create(
                user=request.user,
                activity_type='post_created',
                content=f"Created a new {post.get_post_type_display().lower()}: {post.title}",
                post=post
            )
            
            messages.success(request, _('Post created successfully!'))
            return redirect('community:post_detail', pk=post.pk)
    else:
        post_form = PostForm()
        product = None
        # Only show products by the current user
        if hasattr(request.user, 'artist'):
            post_form.fields['related_product'].queryset = Product.objects.filter(artist__user=request.user)
        else:
            post_form.fields['related_product'].queryset = Product.objects.none()
        
        # Pre-select product if provided in URL
        product_id = request.GET.get('product')
        if product_id:
            try:
                product = Product.objects.get(id=product_id, artist__user=request.user)
                post_form.fields['related_product'].initial = product
            except Product.DoesNotExist:
                product = None
    
    context = {
        'post_form': post_form,
        'product': product,
        'title': _('Create Post'),
    }
    return render(request, 'community/create_post.html', context)

def post_detail(request, pk):
    """View a specific post"""
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('author').prefetch_related('likes', 'replies')
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            # Create activity
            Activity.objects.create(
                user=request.user,
                activity_type='post_commented',
                content=f"Commented on {post.title}",
                post=post
            )
            
            # Create notification for post author
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    message=f"{request.user.username} commented on your post",
                    post=post
                )
            
            messages.success(request, _('Comment added successfully!'))
            return redirect('community:post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'title': post.title,
    }
    return render(request, 'community/post_detail.html', context)

@login_required
def like_post(request, pk):
    """Like/unlike a post"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        
        # Create activity
        Activity.objects.create(
            user=request.user,
            activity_type='post_liked',
            content=f"Liked {post.title}",
            post=post
        )
        
        # Create notification for post author
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                message=f"{request.user.username} liked your post",
                post=post
            )
    
    return JsonResponse({
        'liked': liked,
        'total_likes': post.total_likes()
    })

@login_required
def save_post(request, pk):
    """Save/unsave a post"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.saves.all():
        post.saves.remove(request.user)
        saved = False
    else:
        post.saves.add(request.user)
        saved = True
    
    return JsonResponse({
        'saved': saved,
        'total_saves': post.total_saves()
    })

@login_required
def like_comment(request, pk):
    """Like/unlike a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'total_likes': comment.total_likes()
    })

@login_required
def add_comment(request, pk):
    """Add a comment to a post via AJAX"""
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        content = request.POST.get('content', '').strip()
        
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'content': comment.content,
                'author_name': comment.author.username,
                'author_avatar': comment.author.profile_picture.url if comment.author.profile_picture else '/static/img/default-avatar.png',
                'total_comments': post.comments.count()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Comment content is required'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def delete_comment(request, pk):
    """Delete a comment via AJAX"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        
        # Only allow deletion by comment author or post author
        if comment.author == request.user or comment.post.author == request.user:
            post = comment.post
            comment.delete()
            
            return JsonResponse({
                'success': True,
                'total_comments': post.comments.count()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'You are not authorized to delete this comment'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def accept_connection_from_notification(request, connection_id):
    """Accept connection request from notification page"""
    print(f"Accepting connection {connection_id} for user {request.user.username}")
    print(f"Request method: {request.method}")
    print(f"Request user: {request.user}")
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST requests allowed'
        })
    
    try:
        connection = Connection.objects.get(
            id=connection_id,
            to_user=request.user,
            status='pending'
        )
        print(f"Found connection: {connection}")
        
        # Update connection status
        connection.status = 'accepted'
        connection.save()
        print(f"Connection status updated to: {connection.status}")
        
        # Create notification for the sender
        Notification.objects.create(
            recipient=connection.from_user,
            sender=request.user,
            notification_type='connection_accepted',
            message=f"{request.user.username} accepted your connection request"
        )
        print(f"Notification created for {connection.from_user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Connection request accepted!'
        })
        
    except Connection.DoesNotExist:
        print(f"Connection {connection_id} not found for user {request.user.username}")
        return JsonResponse({
            'success': False,
            'message': 'Connection request not found'
        })
    except Exception as e:
        print(f"Error accepting connection: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
def reject_connection_from_notification(request, connection_id):
    """Reject connection request from notification page"""
    print(f"Rejecting connection {connection_id} for user {request.user.username}")
    print(f"Request method: {request.method}")
    print(f"Request user: {request.user}")
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST requests allowed'
        })
    
    try:
        connection = Connection.objects.get(
            id=connection_id,
            to_user=request.user,
            status='pending'
        )
        print(f"Found connection: {connection}")
        
        # Store sender info before deleting
        sender = connection.from_user
        
        # Delete the connection request
        connection.delete()
        print(f"Connection deleted")
        
        # Create notification for the sender
        Notification.objects.create(
            recipient=sender,
            sender=request.user,
            notification_type='connection_rejected',
            message=f"{request.user.username} declined your connection request"
        )
        print(f"Rejection notification created for {sender.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Connection request rejected'
        })
        
    except Connection.DoesNotExist:
        print(f"Connection {connection_id} not found for user {request.user.username}")
        return JsonResponse({
            'success': False,
            'message': 'Connection request not found'
        })
    except Exception as e:
        print(f"Error rejecting connection: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
def get_notification_counts(request):
    """Get notification and message counts via AJAX"""
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    unread_messages = request.user.received_messages.filter(is_read=False).count()
    
    return JsonResponse({
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages,
    })

@login_required
def connections(request):
    """View user's connections"""
    sent_connections = Connection.objects.filter(from_user=request.user).select_related('to_user')
    received_connections = Connection.objects.filter(to_user=request.user).select_related('from_user')
    
    context = {
        'sent_connections': sent_connections,
        'received_connections': received_connections,
        'title': _('My Connections'),
    }
    return render(request, 'community/connections.html', context)

@login_required
def send_connection_request(request):
    """Send a connection request"""
    if request.method == 'POST':
        form = ConnectionRequestForm(request.POST, user=request.user)
        if form.is_valid():
            connection = form.save(commit=False)
            connection.from_user = request.user
            connection.save()
            
            # Create notification
            Notification.objects.create(
                recipient=connection.to_user,
                sender=request.user,
                notification_type='connection_request',
                message=f"{request.user.username} wants to connect with you"
            )
            
            messages.success(request, _('Connection request sent!'))
            return redirect('community:connections')
    else:
        form = ConnectionRequestForm(user=request.user)
    
    context = {
        'form': form,
        'title': _('Send Connection Request'),
    }
    return render(request, 'community/send_connection_request.html', context)

@login_required
def accept_connection(request, pk):
    """Accept a connection request"""
    connection = get_object_or_404(Connection, pk=pk, to_user=request.user, status='pending')
    connection.status = 'accepted'
    connection.save()
    
    # Create notification
    Notification.objects.create(
        recipient=connection.from_user,
        sender=request.user,
        notification_type='connection_accepted',
        message=f"{request.user.username} accepted your connection request"
    )
    
    messages.success(request, _('Connection accepted!'))
    return redirect('community:connections')

@login_required
def reject_connection(request, pk):
    """Reject a connection request"""
    connection = get_object_or_404(Connection, pk=pk, to_user=request.user, status='pending')
    connection.delete()
    
    messages.success(request, _('Connection request rejected.'))
    return redirect('community:connections')

@login_required
def messages_list(request):
    """List all conversations"""
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related('participants', 'last_message')
    
    context = {
        'conversations': conversations,
        'title': _('Messages'),
    }
    return render(request, 'community/messages_list.html', context)

@login_required
def conversation_detail(request, pk):
    """View a specific conversation"""
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    messages_list = Message.objects.filter(
        Q(sender=request.user, recipient__in=conversation.participants.all()) |
        Q(recipient=request.user, sender__in=conversation.participants.all())
    ).select_related('sender', 'recipient').order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            # Update conversation
            conversation.last_message = message
            conversation.save()
            
            # Create notification
            Notification.objects.create(
                recipient=message.recipient,
                sender=request.user,
                notification_type='message',
                message=f"New message from {request.user.username}",
                message_obj=message
            )
            
            return redirect('community:conversation_detail', pk=conversation.pk)
    else:
        form = MessageForm()
        # Set recipient based on conversation participants
        other_participants = conversation.participants.exclude(id=request.user.id)
        if other_participants.exists():
            form.fields['recipient'].initial = other_participants.first()
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'form': form,
        'title': _('Conversation'),
    }
    return render(request, 'community/conversation_detail.html', context)

@login_required
def notifications(request):
    """View user notifications"""
    notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'post')
    
    # Mark as read
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
        'title': _('Notifications'),
    }
    return render(request, 'community/notifications.html', context)

@login_required
def send_connection_request_ajax(request):
    """Send a connection request (artisan-to-artisan) or follow (customer-to-artisan) via AJAX"""
    if request.method == 'POST':
        to_user_id = request.POST.get('to_user_id')
        try:
            to_user = User.objects.get(id=to_user_id)
            
            # Prevent self-requests
            if to_user == request.user:
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot send request to yourself'
                })
            
            # Determine interaction type based on user roles
            if request.user.role == 'artist' and to_user.role == 'artist':
                # Artisan-to-artisan: Connection request
            existing_connection = Connection.objects.filter(
                Q(from_user=request.user, to_user=to_user) | 
                Q(from_user=to_user, to_user=request.user)
            ).first()
            
            if existing_connection:
                if existing_connection.status == 'pending':
                    return JsonResponse({
                        'success': False,
                        'message': 'Connection request already pending'
                    })
                elif existing_connection.status == 'accepted':
                    return JsonResponse({
                        'success': False,
                        'message': 'Already connected'
                    })
                elif existing_connection.status == 'blocked':
                    return JsonResponse({
                        'success': False,
                        'message': 'Connection blocked'
                    })
            
            # Create new connection request
            connection = Connection.objects.create(
                from_user=request.user,
                to_user=to_user,
                status='pending'
            )
            
            # Create notification
            Notification.objects.create(
                recipient=to_user,
                sender=request.user,
                notification_type='connection_request',
                message=f"{request.user.username} wants to connect with you",
                connection=connection
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Connection request sent!',
                    'status': 'pending',
                    'type': 'connection'
                })
                
            elif request.user.role == 'customer' and to_user.role == 'artist':
                # Customer-to-artisan: Follow
                existing_follow = Follow.objects.filter(
                    follower=request.user,
                    following=to_user
                ).first()
                
                if existing_follow:
                    return JsonResponse({
                        'success': False,
                        'message': 'Already following this artisan'
                    })
                
                # Create new follow
                follow = Follow.objects.create(
                    follower=request.user,
                    following=to_user
                )
                
                # Create notification
                Notification.objects.create(
                    recipient=to_user,
                    sender=request.user,
                    notification_type='follow',
                    message=f"{request.user.username} started following you"
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Now following this artisan!',
                    'status': 'following',
                    'type': 'follow'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid interaction type'
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    })

@login_required
def cancel_connection_request(request):
    """Cancel a pending connection request via AJAX"""
    print(f"Cancel connection request called - Method: {request.method}")
    if request.method == 'POST':
        to_user_id = request.POST.get('to_user_id')
        print(f"Cancel request for user {to_user_id} from user {request.user.id}")
        try:
            to_user = User.objects.get(id=to_user_id)
            
            # Find the pending connection request
            connection = Connection.objects.filter(
                from_user=request.user,
                to_user=to_user,
                status='pending'
            ).first()
            
            if connection:
                print(f"Found connection: {connection.id}, deleting...")
                connection.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Connection request cancelled'
                })
            else:
                print("No pending connection found")
                return JsonResponse({
                    'success': False,
                    'message': 'No pending connection request found'
                })
                
        except User.DoesNotExist:
            print(f"User {to_user_id} not found")
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            })
    
    print("Invalid request method or missing data")
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    })

@login_required
def get_connection_status(request, user_id):
    """Get connection/follow status with a specific user"""
    try:
        other_user = User.objects.get(id=user_id)
        
        # Determine interaction type based on user roles
        if request.user.role == 'artist' and other_user.role == 'artist':
            # Artisan-to-artisan: Check connection status
        connection = Connection.objects.filter(
            Q(from_user=request.user, to_user=other_user) | 
            Q(from_user=other_user, to_user=request.user)
        ).first()
        
        if connection:
            return JsonResponse({
                'status': connection.status,
                    'is_from_me': connection.from_user == request.user,
                    'type': 'connection'
                })
            else:
                return JsonResponse({
                    'status': 'none',
                    'is_from_me': False,
                    'type': 'connection'
                })
                
        elif request.user.role == 'customer' and other_user.role == 'artist':
            # Customer-to-artisan: Check follow status
            follow = Follow.objects.filter(
                follower=request.user,
                following=other_user
            ).first()
            
            if follow:
                return JsonResponse({
                    'status': 'following',
                    'is_from_me': True,
                    'type': 'follow'
                })
            else:
                return JsonResponse({
                    'status': 'none',
                    'is_from_me': False,
                    'type': 'follow'
            })
        else:
            return JsonResponse({
                'status': 'none',
                'is_from_me': False,
                'type': 'none'
            })
            
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        })

@login_required
def unfollow_artisan(request):
    """Unfollow an artisan via AJAX"""
    if request.method == 'POST':
        artisan_id = request.POST.get('artisan_id')
        try:
            artisan = User.objects.get(id=artisan_id, role='artist')
            
            # Check if follow exists
            follow = Follow.objects.filter(
                follower=request.user,
                following=artisan
            ).first()
            
            if follow:
                follow.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Unfollowed successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Not following this artisan'
                })
                
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Artisan not found'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
        })

@login_required
def discover_users(request):
    """Discover new users to connect with"""
    # Get users that are not already connected
    connected_users = Connection.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    ).values_list('from_user', 'to_user')
    
    user_ids = set()
    for from_user, to_user in connected_users:
        user_ids.add(from_user)
        user_ids.add(to_user)
    
    # Exclude current user
    user_ids.discard(request.user.id)
    
    users = User.objects.exclude(id__in=user_ids).filter(role='artist').select_related('artist_profile')[:20]
    
    context = {
        'users': users,
        'title': _('Discover Artists'),
    }
    return render(request, 'community/discover_users.html', context)
