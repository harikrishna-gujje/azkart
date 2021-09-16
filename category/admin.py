from django.contrib import admin
from .models import Category
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug', 'description')
    #list_display_links = ('category_name',)
    ordering = ('-category_name',)
    #readonly_fields = ('last_login', 'date_joined')
    prepopulated_fields = {'slug': ('category_name',)}

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Category, CategoryAdmin)
