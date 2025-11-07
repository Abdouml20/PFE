from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _

from .models import Product
from categories.models import Category

# Create your views here.
def product_list(request):
    products = Product.objects.filter(available=True)
    featured_products = products.filter(featured=True)[:8]
    latest_products = products.order_by('-created_at')[:8]
    
    # Get all craft categories for sidebar
    craft_categories = Product.CRAFT_CHOICES
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'craft_categories': craft_categories,
        'title': _('Home'),
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # Get related products based on craft category instead of regular category
    related_products = []
    if product.craft_category:
        related_products = Product.objects.filter(craft_category=product.craft_category, available=True).exclude(id=product.id)[:4]
    
    # Get craft category name for display
    craft_category_name = dict(Product.CRAFT_CHOICES).get(product.craft_category, '')
    
    context = {
        'product': product,
        'related_products': related_products,
        'craft_category_name': craft_category_name,
        'title': product.name,
    }
    return render(request, 'products/product_detail.html', context)

def product_search(request):
    query = request.GET.get('q', '')
    craft_category = request.GET.get('craft_category', '')
    
    products = Product.objects.filter(available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(artist__name__icontains=query)
        )
    
    if craft_category:
        products = products.filter(craft_category=craft_category)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all craft categories for filtering
    craft_categories = Product.CRAFT_CHOICES
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_craft_category': craft_category,
        'craft_categories': craft_categories,
        'title': _('Search Results'),
    }
    return render(request, 'products/product_search.html', context)
