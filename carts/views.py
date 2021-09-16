from django.shortcuts import render,redirect
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product
from .models import Cart, CartItem

# Create your views here.
def _get_session_id(request):
    if request.session.session_key:
        return request.session.session_key
    else:
        return request.session.create()

def create_or_increment_cart_item(product, cart):
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
    except ObjectDoesNotExist:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
    cart_item.save()
    return cart_item

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_get_session_id(request))
    except ObjectDoesNotExist:
        cart = Cart.objects.create(cart_id=_get_session_id(request))
        cart.save()
    cart_item = create_or_increment_cart_item(product, cart)
    return redirect('cart')

def delete_or_decrement_cart_item(product, cart):
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except ObjectDoesNotExist:
        pass
    return

def remove_from_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_get_session_id(request))
    except ObjectDoesNotExist:
        cart = None
    delete_or_decrement_cart_item(product, cart)
    return redirect('cart')

def cart(request):
    try:
        cart = Cart.objects.get(cart_id=_get_session_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = 0
        for cart_item in cart_items:
            total += cart_item.total()

    except ObjectDoesNotExist:
        cart_items = dict()
        total = 0

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': total*0.03,
        'grand_total': total+total*0.03
    }
    return render(request, 'store/cart.html', context)