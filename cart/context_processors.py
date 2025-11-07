from .models import Cart

def cart(request):
    """
    Context processor to make cart available in all templates
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    elif request.session.session_key:
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    else:
        request.session.create()
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    
    return {'cart': cart}
