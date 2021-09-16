from django.db import models
from category.models import Category
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=255, unique=True)
    product_slug = models.SlugField(max_length=255, unique=True)
    product_img = models.ImageField(upload_to='Photos/products')
    price = models.IntegerField()
    product_desc = models.TextField(blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta():
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.product_name

    def geturl(self):
        return reverse('product_detail', kwargs={
            'category_slug_parameter': self.product_category.slug,
            'product_slug_parameter': self.product_slug
        })