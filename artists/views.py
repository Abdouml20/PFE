from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

from .models import Artist
from products.models import Product
from products.forms import ProductForm, PictureFormSet

# Create your views here.
def artist_list(request):
    artists = Artist.objects.filter(availability=True)
    
    # Pagination
    paginator = Paginator(artists, 12)  # Show 12 artists per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': _('Artists'),
    }
    return render(request, 'artists/artist_list.html', context)

def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    products = Product.objects.filter(artist=artist, available=True)
    
    # Pagination
    paginator = Paginator(products, 8)  # Show 8 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'artist': artist,
        'page_obj': page_obj,
        'title': artist.name,
    }
    return render(request, 'artists/artist_detail.html', context)

@login_required
def artist_dashboard(request):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get or create artist profile
    artist, created = Artist.objects.get_or_create(
        user=request.user,
        defaults={'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username}
    )
    
    # Get artist's products
    products = Product.objects.filter(artist=artist)
    
    # Calculate counts for dashboard stats
    available_products_count = products.filter(available=True).count()
    featured_products_count = products.filter(featured=True).count()
    
    context = {
        'artist': artist,
        'products': products,
        'available_products_count': available_products_count,
        'featured_products_count': featured_products_count,
        'title': _('Artist Dashboard'),
    }
    return render(request, 'artists/artist_dashboard.html', context)

@login_required
def add_product(request):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = PictureFormSet(request.POST, request.FILES, instance=None)
        
        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.artist = artist
            # Set category to None since we're not using it anymore
            product.category = None
            product.save()
            
            # Save pictures
            pictures = formset.save(commit=False)
            for picture in pictures:
                picture.product = product
                picture.artist = artist
                picture.save()
            
            messages.success(request, _('Product added successfully!'))
            
            # Check if user wants to create a post about this product
            create_post = request.POST.get('create_post', 'false')
            if create_post == 'true':
                # Redirect to create post page with product ID
                return redirect(f"{reverse('community:create_post')}?product={product.id}")
            else:
                return redirect('artists:artist_dashboard')
    else:
        form = ProductForm()
        formset = PictureFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': _('Add Product'),
    }
    return render(request, 'artists/product_form.html', context)

@login_required
def edit_product(request, pk):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get product
    product = get_object_or_404(Product, pk=pk, artist=artist)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = PictureFormSet(request.POST, request.FILES, instance=product)
        
        if form.is_valid() and formset.is_valid():
            product = form.save()
            pictures = formset.save(commit=False)
            for picture in pictures:
                picture.product = product
                picture.artist = artist
                picture.save()
            # Delete any removed images
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, _('Product updated successfully!'))
            return redirect('artists:artist_dashboard')
    else:
        form = ProductForm(instance=product)
        formset = PictureFormSet(instance=product)
    
    context = {
        'form': form,
        'formset': formset,
        'product': product,
        'title': _('Edit Product'),
    }
    return render(request, 'artists/product_form.html', context)

@login_required
def delete_product(request, pk):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get product
    product = get_object_or_404(Product, pk=pk, artist=artist)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, _('Product deleted successfully!'))
        return redirect('artists:artist_dashboard')
    
    context = {
        'product': product,
        'title': _('Delete Product'),
    }
    return render(request, 'artists/product_confirm_delete.html', context)

@login_required
def toggle_product_availability(request, pk):
    # Check if user is an artist
    if request.user.role != 'artist':
        return JsonResponse({'success': False, 'message': _('You do not have permission to perform this action.')}, status=403)
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get product
    product = get_object_or_404(Product, pk=pk, artist=artist)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product.available = data.get('available', not product.available)
            product.save()
            
            return JsonResponse({
                'success': True,
                'available': product.available,
                'message': _('Product availability updated successfully!')
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': _('Invalid request method')}, status=405)
