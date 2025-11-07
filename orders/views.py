from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
import json

from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.models import Cart
from cart.views import _get_cart
from artists.models import Artist
from products.models import Product

# Create your views here.
@login_required
def order_create(request):
    cart = _get_cart(request)
    wilaya_shipping_prices = {
        'adrar': 500, 'chlef': 600, 'laghouat': 700, 'oum-el-bouaghi': 800, 'batna': 900, 'bejaia': 1000,
        'biskra': 1100, 'bechar': 1200, 'blida': 1300, 'bouira': 1400, 'tamanrasset': 1500, 'tebessa': 1600,
        'tlemcen': 1700, 'tiaret': 1800, 'tizi-ouzou': 1900, 'algiers': 2000, 'djelfa': 2100, 'jijel': 2200,
        'setif': 2300, 'saida': 2400, 'skikda': 2500, 'sidi-bel-abbes': 2600, 'annaba': 2700, 'guelma': 2800,
        'constantine': 2900, 'medea': 3000, 'mostaganem': 3100, 'msila': 3200, 'mascara': 3300, 'ouargla': 3400,
        'oran': 3500, 'el-bayadh': 3600, 'illizi': 3700, 'bordj-bou-arreridj': 3800, 'boumerdes': 3900,
        'el-tarf': 4000, 'tindouf': 4100, 'tissemsilt': 4200, 'el-oued': 4300, 'khenchela': 4400, 'souk-ahras': 4500,
        'tipaza': 4600, 'mila': 4700, 'ain-defla': 4800, 'naama': 4900, 'ain-temouchent': 5000, 'ghardaia': 5100,
        'relizane': 5200, 'timimoun': 5300, 'bordj-badji-mokhtar': 5400, 'ouled-djellal': 5500, 'beni-abbes': 5600,
        'in-salah': 5700, 'in-guezzam': 5800, 'touggourt': 5900, 'djanet': 6000, 'el-mghair': 6100, 'el-menia': 6200,
    }
    shipping_details = []
    shipping_total = 0
    customer_wilaya = request.user.wilaya if request.user.is_authenticated else None
    if cart.items.exists() and customer_wilaya:
        for item in cart.items.all():
            artist = getattr(item.product.artist, 'user', None)
            agency = artist.delivery_agency if artist and artist.role == 'artist' else None
            wilaya = customer_wilaya
            shipping_price = wilaya_shipping_prices.get(wilaya, 0) if agency else 0
            shipping_details.append({
                'item': item,
                'agency': agency,
                'shipping_price': shipping_price,
            })
            shipping_total += shipping_price
    context = {
        'form': None,
        'cart': cart,
        'shipping_details': shipping_details,
        'shipping_total': shipping_total,
        'title': _('Checkout'),
    }
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.discount_price or item.product.price,
                    quantity=item.quantity
                )
            cart.items.all().delete()
            messages.success(request, _('Order placed successfully!'))
            return redirect('orders:order_detail', pk=order.id)
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'wilaya': request.user.wilaya,
        }
        form = OrderCreateForm(initial=initial_data)
    context['form'] = form
    return render(request, 'orders/order_create.html', context)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)
    
    context = {
        'order': order,
        'title': _('Order Detail'),
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'title': _('Order History'),
    }
    return render(request, 'orders/order_history.html', context)

# Artist Order Management Views
@login_required
def artist_orders(request):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get all orders containing products by this artist
    artist_products = Product.objects.filter(artist=artist)
    
    # Get order items for this artist's products
    order_items = OrderItem.objects.filter(product__in=artist_products)
    
    # Get unique orders
    order_ids = order_items.values_list('order_id', flat=True).distinct()
    orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Stats
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    processing_orders = orders.filter(status='processing').count()
    shipped_orders = orders.filter(status='shipped').count()
    delivered_orders = orders.filter(status='delivered').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    context = {
        'orders': orders,
        'order_items': order_items,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'title': _('Manage Orders'),
    }
    return render(request, 'orders/artist_orders.html', context)

@login_required
def artist_order_detail(request, pk):
    # Check if user is an artist
    if request.user.role != 'artist':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('users:dashboard')
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get order
    order = get_object_or_404(Order, id=pk)
    
    # Get artist's products in this order
    artist_products = Product.objects.filter(artist=artist)
    order_items = order.items.filter(product__in=artist_products)
    
    # Check if artist has products in this order
    if not order_items.exists():
        messages.error(request, _('You do not have any products in this order.'))
        return redirect('orders:artist_orders')
    
    # Calculate subtotal for artist's items
    artist_subtotal = sum(item.get_cost() for item in order_items)
    
    context = {
        'order': order,
        'order_items': order_items,
        'artist_subtotal': artist_subtotal,
        'title': _('Order Detail'),
    }
    return render(request, 'orders/artist_order_detail.html', context)

@login_required
def update_order_status(request, pk):
    # Check if user is an artist
    if request.user.role != 'artist':
        return JsonResponse({'success': False, 'message': _('You do not have permission to perform this action.')}, status=403)
    
    # Get artist profile
    artist = get_object_or_404(Artist, user=request.user)
    
    # Get order
    order = get_object_or_404(Order, id=pk)
    
    # Get artist's products in this order
    artist_products = Product.objects.filter(artist=artist)
    order_items = order.items.filter(product__in=artist_products)
    
    # Check if artist has products in this order
    if not order_items.exists():
        return JsonResponse({'success': False, 'message': _('You do not have any products in this order.')}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            # Validate status
            valid_statuses = [status[0] for status in Order.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({'success': False, 'message': _('Invalid status.')}, status=400)
            
            # Update order status
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status,
                'message': _('Order status updated successfully!')
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': _('Invalid request method')}, status=405)
