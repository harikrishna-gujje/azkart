from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from store.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.
def _get_session_id(request):
    if request.session.session_key:
        return request.session.session_key
    else:
        return request.session.create()

def create_or_increment_cart_item(product, cart, variations_for_product):
    try:
        cart_items = CartItem.objects.filter(product=product, cart=cart)  # cart items of same prod with diff variations
        existing_variations = list()
        if len(variations_for_product) > 0:
            for cart_item in cart_items:

                existing_variations.append(list(cart_item.variations_for_product.all()))
            # print(existing_variations)
            # print(variations_for_product)
            # if variations_for_product.sort(key=lambda x: x.variation_value) in existing_variations.sort(key=lambda x: x.variation_value):
            #     return HttpResponse('existing variation')
        # cart_item.save()
        # cart_item.quantity += 1
        # cart_item.save()
    except ObjectDoesNotExist:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if len(variations_for_product) > 0:
            for variation in variations_for_product:
                cart_item.variations_for_product.add(variation)
        cart_item.save()
    return

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    variations_for_product = list()
    if request.method == 'POST':
        for key, value in request.POST.items():  # request.POST is a dictionary of all the values received.
            try:
                variation = Variation.objects.get(product=product, variation_category=key, variation_value=value)
                variations_for_product.append(variation)  # now we are getting variations for this product,
                # we only have to add it to the cart item so, making a field in cart item model to store variations.
            except ObjectDoesNotExist:
                pass
    try:
        cart = Cart.objects.get(cart_id=_get_session_id(request))
    except ObjectDoesNotExist:
        cart = Cart.objects.create(cart_id=_get_session_id(request))
        cart.save()
    create_or_increment_cart_item(product, cart, variations_for_product)
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