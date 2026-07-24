"""
Product listing and detail views.
Category pages: cold drinks, soft drinks, wines.
Product detail with add to cart.
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category


def product_list(request, category_slug=None):
    """
    List products, optionally filtered by category.
    Used for cold drinks, soft drinks, wines pages.
    Supports search (q) and filter by price (min_price, max_price).
    """
    products = Product.objects.filter(in_stock=True).select_related('category')
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

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
        'categories': categories,
        'search_query': q,
        'min_price': min_price,
        'max_price': max_price,
    })


def product_detail(request, slug):
    """Product detail page with full info and add to cart."""
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})
