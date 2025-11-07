from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from .models import Cart, CartItem
from products.models import Product

# Create your views here.
def _get_cart(request):
    """Helper function to get or create cart"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    elif request.session.session_key:
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    else:
        request.session.create()
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    return cart

def cart_detail(request):
    cart = _get_cart(request)
    
    context = {
        'cart': cart,
        'title': _('Shopping Cart'),
    }
    return render(request, 'cart/cart_detail.html', context)

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = _get_cart(request)
    
    # Check if the user is an artist and trying to add their own product
    if request.user.is_authenticated and request.user.role == 'artist':
        # Get the artist profile associated with the user
        from artists.models import Artist
        try:
            artist = Artist.objects.get(user=request.user)
            # Check if the product belongs to the artist
            if product.artist == artist:
                error_message = _('You cannot add your own products to your cart.')
                messages.error(request, error_message)
                
                # Handle AJAX requests
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                    })
                
                # Get the next parameter or default to product detail
                next_url = request.POST.get('next', 'products:product_detail')
                return redirect(next_url, slug=product.slug)
        except Artist.DoesNotExist:
            # If the user is marked as an artist but doesn't have an artist profile yet
            pass
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if product already in cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, _('Cart updated successfully!'))
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        messages.success(request, _('Product added to cart!'))
    
    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_cost': cart.get_total_cost(),
        })
    
    # Get the next parameter or default to cart detail
    next_url = request.POST.get('next', 'cart:cart_detail')
    return redirect(next_url)

def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        messages.success(request, _('Product removed from cart!'))
    except CartItem.DoesNotExist:
        pass
    
    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_cost': cart.get_total_cost(),
        })
    
    return redirect('cart:cart_detail')

def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, _('Cart updated successfully!'))
        else:
            cart_item.delete()
            messages.success(request, _('Product removed from cart!'))
    except CartItem.DoesNotExist:
        if quantity > 0:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            messages.success(request, _('Product added to cart!'))
        else:
            cart_item = None
    
    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_cost = cart_item.get_cost() if cart_item else 0
        
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_cost': cart.get_total_cost(),
            'item_cost': item_cost,
        })
    
    return redirect('cart:cart_detail')
