"""
Product listing, detail views, and age verification endpoint.
Supports combined category pages and backend age gating for wine products.
"""

import json
from urllib.parse import quote
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Category


def is_age_verified(request):
    """
    Check if the current request is age-verified for wines.
    Checks Django session, cookies, and user customer profile.
    """
    if request.session.get('age_verified') is True:
        return True
    if request.COOKIES.get('age_verified') == 'true':
        return True
    if request.user.is_authenticated:
        profile = getattr(request.user, 'customerprofile', None)
        if profile and profile.is_adult:
            return True
    return False


def verify_age(request):
    """
    Endpoint for processing age verification responses from the age-gate modal.
    Sets Django session and cookie for session-persisted access.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            choice = data.get('choice', '')
        except (json.JSONDecodeError, AttributeError):
            choice = request.POST.get('choice', '')

        if choice in ['over18', 'yes', 'over_18']:
            request.session['age_verified'] = True
            response = JsonResponse({'status': 'success', 'verified': True})
            response.set_cookie('age_verified', 'true', max_age=86400 * 30, httponly=False, samesite='Lax')
            return response
        else:
            request.session['age_verified'] = False
            messages.info(
                request,
                'Sorry, wine products are only available to customers aged 18 years or older.'
            )
            response = JsonResponse({
                'status': 'denied',
                'verified': False,
                'message': 'Sorry, wine products are only available to customers aged 18 years or older.',
                'redirect': reverse('main:home')
            })
            response.set_cookie('age_verified', 'false', max_age=86400, httponly=False, samesite='Lax')
            return response

    return JsonResponse({'verified': is_age_verified(request)})


def product_list(request, category_slug=None):
    """
    List products, optionally filtered by category.
    Supports individual categories and combined category pages:
    - soft-cold-drinks (Soft Drinks & Cold Drinks)
    - tea-coffee (Tea & Coffee)
    - wines (Wines - Protected by Age Gate)
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
            # Age gate check
            if not is_age_verified(request):
                messages.warning(request, 'You must be at least 18 years old to enter the Wines section.')
                home_url = reverse('main:home')
                return redirect(f"{home_url}?age_gate=wines&next={quote(request.path)}")
            category = get_object_or_404(Category, slug='wines')
            products = products.filter(category=category)
            category_title = category.name
        else:
            category = get_object_or_404(Category, slug=category_slug)
            if category.slug == 'wines' and not is_age_verified(request):
                messages.warning(request, 'You must be at least 18 years old to enter the Wines section.')
                home_url = reverse('main:home')
                return redirect(f"{home_url}?age_gate=wines&next={quote(request.path)}")
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
    """Product detail page with backend age protection for wines."""
    product = get_object_or_404(Product, slug=slug)

    # Protect wine detail pages
    if product.is_wine and not is_age_verified(request):
        messages.warning(request, 'You must be at least 18 years old to view wine products.')
        home_url = reverse('main:home')
        return redirect(f"{home_url}?age_gate=wines&next={quote(request.path)}")

    return render(request, 'products/product_detail.html', {'product': product})
