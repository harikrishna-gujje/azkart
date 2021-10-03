from django.core.exceptions import ObjectDoesNotExist

from .models import Cart, CartItem
from .views import _get_session_id

def number_of_cart_items(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_get_session_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
    except ObjectDoesNotExist:
        return dict(cart_items_count=0)
    for _ in cart_items:
        count += 1
    return dict(cart_items_count=count)
