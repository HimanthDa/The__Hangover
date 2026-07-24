"""
Views for main pages: Home, About, Contact, Drink History, Wine History.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product


def home(request):
    """Home page with banner and grouped drink sections."""
    tea_coffee_products = Product.objects.filter(
        in_stock=True,
        category__slug__in=['tea', 'coffee', 'teas', 'coffees'],
    ).select_related('category').order_by('-featured', 'name')

    soft_cold_products = Product.objects.filter(
        in_stock=True,
        category__slug__in=['soft-drinks', 'cold-drinks'],
    ).select_related('category').order_by('-featured', 'name')

    wine_products = Product.objects.filter(
        in_stock=True,
        category__slug='wines',
    ).select_related('category').order_by('-featured', 'name')

    return render(request, 'main/home.html', {
        'tea_coffee_products': tea_coffee_products,
        'soft_cold_products': soft_cold_products,
        'wine_products': wine_products,
    })


def about(request):
    """About page - beverages and wine culture."""
    return render(request, 'main/about.html')


def contact(request):
    """Contact page. Can be extended with a contact form and email."""
    return render(request, 'main/contact.html')


def drink_history(request):
    """Informational page about the history of beverages."""
    return render(request, 'main/drink_history.html')


def wine_history(request):
    """Informational page about wine history, types, regions, timeline."""
    return render(request, 'main/wine_history.html')


def site_history(request):
    """The Hangover history page (brand + website story)."""
    return render(request, 'main/site_history.html')
