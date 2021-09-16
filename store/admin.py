from django.contrib import admin
from .models import Product

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_slug', 'product_img', 'price', 'product_desc', 'modified_date',
                    'product_category')
    prepopulated_fields = {'product_slug': ('product_name',)}

admin.site.register(Product, ProductAdmin)
