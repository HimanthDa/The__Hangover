"""
Views for main pages: Home, About, Contact, Drink History, Wine History.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product, Category


def home(request):
    """Home page with banner, featured drinks, and categories."""
    featured = Product.objects.filter(featured=True, in_stock=True)[:8]
    categories = Category.objects.all()
    return render(request, 'main/home.html', {
        'featured': featured,
        'categories': categories,
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
