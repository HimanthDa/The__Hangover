"""
Cart views: view cart, add, update quantity, remove, and cart history.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from accounts.models import CustomerProfile
from .models import CartHistory
from .utils import get_cart_items, add_to_cart, update_cart_item, remove_from_cart


def _known_underage_for_wine(user):
    if not user.is_authenticated:
        return False
    try:
        profile = user.customer_profile
    except CustomerProfile.DoesNotExist:
        return False
    return profile.date_of_birth and not profile.is_adult


def cart_view(request):
    """Shopping cart page."""
    items = get_cart_items(request)
    subtotal = sum(item['line_total'] for item in items)
    return render(request, 'cart/cart.html', {
        'cart_items': items,
        'subtotal': subtotal,
    })


@require_POST
def cart_add(request, product_id):
    """Add product to cart (POST)."""
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    product = get_object_or_404(Product, pk=product_id)
    if product.is_wine and _known_underage_for_wine(request.user):
        messages.error(request, 'You must be 18 or older to add wine products to your cart.')
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'main:home'
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('main:home')

    if add_to_cart(request, product_id, quantity):
        messages.success(request, 'Item added to cart.')
    else:
        messages.error(request, 'Product not found or out of stock.')
    # Redirect back to referrer or product detail
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'main:home'
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect('main:home')


@require_POST
def cart_update(request, product_id):
    """Update quantity in cart (POST)."""
    quantity = int(request.POST.get('quantity', 0))
    update_cart_item(request, product_id, quantity)
    messages.info(request, 'Cart updated.')
    return redirect('cart:cart')


@require_POST
def cart_remove(request, product_id):
    """Remove item from cart (POST)."""
    remove_from_cart(request, product_id)
    messages.info(request, 'Item removed from cart.')
    return redirect('cart:cart')


@login_required(login_url='accounts:login')
def cart_history_view(request):
    """View customer's cart history."""
    history_items = CartHistory.objects.filter(user=request.user).select_related('product').order_by('-updated_at')
    return render(request, 'cart/cart_history.html', {
        'history_items': history_items,
    })


@login_required(login_url='accounts:login')
@require_POST
def cart_history_readd(request, history_id):
    """Re-add an item from cart history back into current active cart."""
    item = get_object_or_404(CartHistory, id=history_id, user=request.user)
    if item.product and item.product.is_wine and _known_underage_for_wine(request.user):
        messages.error(request, 'You must be 18 or older to add wine products to your cart.')
        return redirect('cart:cart')

    if item.product and item.product.in_stock:
        add_to_cart(request, item.product.id, item.quantity)
        messages.success(request, f'Added {item.product.name} (x{item.quantity}) back to your cart.')
    else:
        messages.warning(request, f'{item.product.name if item.product else "Item"} is currently out of stock.')
    return redirect('cart:cart')
