"""
Product listing and detail views.
Supports individual and combined category pages.
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category


def is_age_verified(request):
    """Bypassed helper for backwards compatibility."""
    return True


def verify_age(request):
    """Endpoint kept for backwards compatibility."""
    return JsonResponse({'status': 'success', 'verified': True})


def product_list(request, category_slug=None):
    """
    List products, optionally filtered by category.
    Supports individual categories and combined category pages:
    - soft-cold-drinks (Soft Drinks & Cold Drinks)
    - tea-coffee (Tea & Coffee)
    - wines (Wines)
    """
    products = Product.objects.filter(in_stock=True).select_related('category')
    category = None
    category_title = None

    if category_slug:
        slug_lower = category_slug.lower()

        if slug_lower in ['soft-cold-drinks', 'soft-drinks-cold-drinks', 'soft-and-cold-drinks']:
            products = products.filter(category__slug__in=['soft-drinks', 'cold-drinks'])
            category_title = "Soft Drinks & Cold Drinks"
        elif slug_lower in ['tea-coffee', 'teas-coffees', 'tea-and-coffee']:
            products = products.filter(category__slug__in=['tea', 'coffee'])
            category_title = "Tea & Coffee"
        elif slug_lower in ['wines', 'wine']:
            category = get_object_or_404(Category, slug='wines')
            products = products.filter(category=category)
            category_title = category.name
        else:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
            category_title = category.name

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(brand__icontains=q) | Q(description__icontains=q)
        )

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    products = products.order_by('name')
    categories = Category.objects.all()

    return render(request, 'products/product_list.html', {
        'products': products,
        'category': category,
        'category_title': category_title,
        'category_slug': category_slug,
        'categories': categories,
        'search_query': q,
        'min_price': min_price,
        'max_price': max_price,
    })


def product_detail(request, slug):
    """Product detail page with full info and add to cart."""
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})
