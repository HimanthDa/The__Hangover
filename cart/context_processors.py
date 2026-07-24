"""
Context processor to expose cart total and count in all templates.
"""

from .utils import get_cart


def cart_total(request):
    """Add cart_count and cart_total to template context safely."""
    try:
        cart = get_cart(request)
        if not isinstance(cart, dict):
            return {'cart_count': 0, 'cart_total': 0.0}
        count = 0
        total = 0.0
        for item in cart.values():
            if isinstance(item, dict):
                try:
                    q = int(item.get('quantity', 0))
                    p = float(item.get('price', 0.0))
                    count += q
                    total += p * q
                except (ValueError, TypeError):
                    continue
        return {
            'cart_count': count,
            'cart_total': round(total, 2),
        }
    except Exception:
        return {
            'cart_count': 0,
            'cart_total': 0.0,
        }

