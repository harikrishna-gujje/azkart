from django.db import models
from store.models import Product, Variation

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations_for_product = models.ManyToManyField(Variation, blank=True)  # same product can be added with diff
    # variation to cartitem
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Foreign key can be one to one or one to many field
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name
