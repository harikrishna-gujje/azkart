from django.contrib import admin
from .models import Product, Variation

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_slug', 'product_img', 'price', 'product_desc', 'modified_date',
                    'product_category')
    prepopulated_fields = {'product_slug': ('product_name',)}


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_available')
    list_editable = ('is_available',)
    list_filter = ('variation_category', 'variation_value', 'is_available')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
