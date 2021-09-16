from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .models import Product
from category.models import Category
from carts.models import Cart, CartItem
from carts.views import _get_session_id


# Create your views here.

def store(request, category_slug_parameter=None):

    if category_slug_parameter != None:
        category = get_object_or_404(Category, slug=category_slug_parameter)
        products = Product.objects.all().filter(product_category=category, is_available=True)
        products_count = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        products_count = products.count()

    context = {
        'products': products,
        'products_count': products_count
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug_parameter=None, product_slug_parameter=None):
    context = dict()
    try:
        cat = get_object_or_404(Category, slug=category_slug_parameter)
        for product in Product.objects.all().filter(product_category=cat):
            if product.product_slug == product_slug_parameter:
                context = {
                    'single_product': product
                }
                break

    except Exception as e:
        raise e
    # checking whether the product is added to cart or not
    product = get_object_or_404(Product, product_slug=product_slug_parameter)
    cart = Cart.objects.get(cart_id=_get_session_id(request))
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        context['is_in_cart'] = True
    except ObjectDoesNotExist:
        context['is_in_cart'] = False

    return render(request, 'store/product_detail.html', context)
