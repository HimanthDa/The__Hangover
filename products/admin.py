"""
Admin panel for products and categories.
Admin can add/edit/delete drinks, upload images, manage prices.
"""

from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'in_stock', 'featured', 'created_at')
    list_filter = ('category', 'featured', 'in_stock')
    search_fields = ('name', 'brand', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'brand', 'price', 'description')
        }),
        ('Details', {
            'fields': ('ingredients', 'history', 'country_of_origin', 'alcohol_percentage')
        }),
        ('Media & Status', {
            'fields': ('image', 'featured', 'in_stock')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
