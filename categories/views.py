from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.defaulttags import register

from .models import Category
from products.models import Product
from artists.models import Artist
from .forms import CategoryForm

# Template filter to access dictionary with variable key
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

# Default images for craft categories from the internet
DEFAULT_CATEGORY_IMAGES = {
    'traditional': 'https://i.etsystatic.com/18774905/r/il/a7c1e0/3544071326/il_794xN.3544071326_4iqe.jpg',
    'clothing': 'https://i.pinimg.com/originals/a9/33/9f/a9339f482fe3a1a9b9e9a363e0a9e888.jpg',
    'accessories': 'https://i.etsystatic.com/16021186/r/il/c7a7d7/1432516557/il_794xN.1432516557_cqvl.jpg',
    'jewelry': 'https://i.etsystatic.com/5977438/r/il/9d5c28/3137223413/il_794xN.3137223413_7gu7.jpg',
    'home-decor': 'https://i.etsystatic.com/14048289/r/il/9f8e0a/3242715054/il_794xN.3242715054_8a9h.jpg',
    'crockery': 'https://i.etsystatic.com/5977438/r/il/9d5c28/3137223413/il_794xN.3137223413_7gu7.jpg',
    'toys-games': 'https://i.etsystatic.com/14048289/r/il/9f8e0a/3242715054/il_794xN.3242715054_8a9h.jpg',
    'art-painting': 'https://i.etsystatic.com/16021186/r/il/c7a7d7/1432516557/il_794xN.1432516557_cqvl.jpg',
    'gift-ideas': 'https://i.etsystatic.com/18774905/r/il/a7c1e0/3544071326/il_794xN.3544071326_4iqe.jpg',
}

# Create your views here.
def category_list(request):
    # Redirect to craft categories instead of regular categories
    return redirect('categories:craft_category_list')

def craft_category_list(request):
    # Get craft categories from Product model choices
    craft_categories = Product.CRAFT_CHOICES
    
    # Count products for each craft category
    craft_products_count = {}
    for craft_id, craft_name in craft_categories:
        craft_products_count[craft_id] = Product.objects.filter(craft_category=craft_id, available=True).count()
    
    context = {
        'craft_categories': craft_categories,
        'craft_products_count': craft_products_count,
        'title': _('Craft Categories'),
    }
    return render(request, 'categories/craft_category_list.html', context)

def category_detail(request, slug):
    # Redirect to craft categories since we're not using regular categories anymore
    return redirect('categories:craft_category_list')

def craft_category_detail(request, craft_id):
    # Get craft name from choices
    craft_name = dict(Product.CRAFT_CHOICES).get(craft_id, '')
    if not craft_name:
        return redirect('categories:craft_category_list')
    
    # Get products for this craft category
    products = Product.objects.filter(craft_category=craft_id, available=True)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'craft_id': craft_id,
        'craft_name': craft_name,
        'products': products,
        'page_obj': page_obj,
        'title': craft_name,
    }
    return render(request, 'categories/craft_category_detail.html', context)

@login_required
def add_category(request):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, _('Category added successfully!'))
            return redirect('categories:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': _('Add Category'),
    }
    return render(request, 'categories/category_form.html', context)

@login_required
def edit_category(request, pk):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get category
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('Category updated successfully!'))
            return redirect('categories:category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': _('Edit Category'),
    }
    return render(request, 'categories/category_form.html', context)

@login_required
def delete_category(request, pk):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get category
    category = get_object_or_404(Category, pk=pk)
    
    # Check if category has products
    products_count = Product.objects.filter(category=category).count()
    
    if request.method == 'POST':
        if products_count > 0:
            messages.error(request, _('Cannot delete category with products. Please reassign or delete the products first.'))
            return redirect('categories:category_list')
        
        category.delete()
        messages.success(request, _('Category deleted successfully!'))
        return redirect('categories:category_list')
    
    context = {
        'category': category,
        'products_count': products_count,
        'title': _('Delete Category'),
    }
    return render(request, 'categories/category_confirm_delete.html', context)
