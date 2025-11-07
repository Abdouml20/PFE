from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q

from .models import User
from .forms import UserRegistrationForm, UserProfileForm
from orders.models import Order
from community.models import Follow, Connection

# Create your views here.
@csrf_protect
def register(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, _('Your account has been created! You can now log in.'))
            return redirect('account_login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form, 'title': _('Register')})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Get follower and connection counts for artists
    follower_count = 0
    connection_count = 0
    
    if request.user.role == 'artist':
        follower_count = Follow.objects.filter(following=request.user).count()
        connection_count = Connection.objects.filter(
            Q(from_user=request.user, status='accepted') | 
            Q(to_user=request.user, status='accepted')
        ).count()
    
    context = {
        'user': request.user,
        'orders': orders,
        'follower_count': follower_count,
        'connection_count': connection_count,
        'title': _('My Profile'),
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated!'))
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'title': _('Edit Profile'),
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def dashboard(request):
    # Different dashboard views based on user role
    if request.user.role == 'artist':
        return redirect('artists:artist_dashboard')
    
    # For regular customers, redirect to profile page
    return redirect('users:profile')
