from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from store.models import Product, Variation
from .models import Cart, CartItem


# Create your views here.
def _get_session_id(request):
    if request.session.session_key:
        return request.session.session_key
    else:
        return request.session.create()


def create_or_increment_cart_item_for_user(product, user, variations_for_product):
    """ to create a new cart_item or to increment if it exists for the current user"""
    if CartItem.objects.filter(product=product, user=user).exists():
        cart_items = CartItem.objects.filter(product=product, user=user)  # cart items of same prod with diff variations
        existing_variations = list()
        cart_ids = list()
        if len(variations_for_product) > 0:
            for cart_item in cart_items:
                existing_variations.append(list(cart_item.variations_for_product.all()))
                cart_ids.append(cart_item.id)
            reverse_of_variations = [0, 1]
            reverse_of_variations[0], reverse_of_variations[1] = variations_for_product[1], variations_for_product[0]
            if (variations_for_product in existing_variations) or (reverse_of_variations in existing_variations):
                try:
                    index = existing_variations.index(variations_for_product)
                except:
                    index = existing_variations.index(reverse_of_variations)
                cartitem_id_of_existing_product = cart_ids[index]
                cart_item = CartItem.objects.get(id=cartitem_id_of_existing_product)
                cart_item.quantity += 1
                cart_item.save()
                return
            else:
                cart_item = CartItem.objects.create(product=product, user=user, quantity=1)
                if len(variations_for_product) > 0:
                    for variation in variations_for_product:
                        cart_item.variations_for_product.add(variation)
                cart_item.save()

    else:
        cart_item = CartItem.objects.create(product=product, user=user, quantity=1)
        if variations_for_product:
            for variation in variations_for_product:
                cart_item.variations_for_product.add(variation)
        cart_item.save()
    return


def create_or_increment_cart_item(product, cart, variations_for_product):
    """ to create a new cart_item or to increment if it exists"""
    if CartItem.objects.filter(product=product, cart=cart).exists():
        cart_items = CartItem.objects.filter(product=product, cart=cart)  # cart items of same prod with diff variations
        existing_variations = list()
        cart_ids = list()
        if len(variations_for_product) > 0:
            for cart_item in cart_items:
                existing_variations.append(list(cart_item.variations_for_product.all()))
                cart_ids.append(cart_item.id)
            reverse_of_variations = [0, 1]
            reverse_of_variations[0], reverse_of_variations[1] = variations_for_product[1], variations_for_product[0]
            if (variations_for_product in existing_variations) or (reverse_of_variations in existing_variations):
                try:
                    index = existing_variations.index(variations_for_product)
                except:
                    index = existing_variations.index(reverse_of_variations)
                cartitem_id_of_existing_product = cart_ids[index]
                cart_item = CartItem.objects.get(id=cartitem_id_of_existing_product)
                cart_item.quantity += 1
                cart_item.save()
                return
            else:
                cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if len(variations_for_product) > 0:
                    for variation in variations_for_product:
                        cart_item.variations_for_product.add(variation)
                cart_item.save()

    else:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if variations_for_product:
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
    if request.user.is_authenticated:
        create_or_increment_cart_item_for_user(product, request.user, variations_for_product)
    else:
        try:
            cart = Cart.objects.get(cart_id=_get_session_id(request))
        except ObjectDoesNotExist:
            cart = Cart.objects.create(cart_id=_get_session_id(request))
            cart.save()
        create_or_increment_cart_item(product, cart, variations_for_product)
    return redirect('cart')


def delete_or_decrement_cart_item(product, cart_item_id):
    try:
        cart_item = CartItem.objects.get(product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except ObjectDoesNotExist:
        pass
    return


def remove_from_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    delete_or_decrement_cart_item(product, cart_item_id)
    return redirect('cart')


def remove_cart_item_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total = 0
        for cart_item in cart_items:
            total += cart_item.total()
    else:
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


@login_required(login_url='login')
def checkout(request):
    try:
        # you have to login to reach this.
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total = 0
        for cart_item in cart_items:
            total += cart_item.total()

    except ObjectDoesNotExist:
        cart_items = dict()
        total = 0

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': total * 0.03,
        'grand_total': total + total * 0.03
    }
    return render(request, 'store/checkout.html', context)