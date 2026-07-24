"""
Cart stored in session: { product_id: { quantity, price, name, image_url } }
"""

from products.models import Product


CART_SESSION_KEY = 'cart'


def get_cart(request):
    """Return the cart dict from session."""
    if not hasattr(request, 'session'):
        return {}
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart):
    """Save cart dict to session."""
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def add_to_cart(request, product_id, quantity=1):
    """Add or update quantity for a product in cart."""
    try:
        product = Product.objects.get(pk=product_id, in_stock=True)
    except Product.DoesNotExist:
        return False
    cart = get_cart(request)
    pid = str(product.id)
    if pid in cart:
        cart[pid]['quantity'] += quantity
    else:
        cart[pid] = {
            'quantity': quantity,
            'price': str(product.price),
            'name': product.name,
            'image_url': product.image_url if hasattr(product, 'image_url') else '',
        }
    save_cart(request, cart)

    # If user is authenticated, save/update CartHistory record
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            from .models import CartHistory
            cart_item_qty = cart[pid]['quantity']
            CartHistory.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'quantity': cart_item_qty,
                    'price': product.price,
                }
            )
        except Exception:
            pass

    return True


def update_cart_item(request, product_id, quantity):
    """Set quantity for a cart item. Remove if quantity <= 0."""
    cart = get_cart(request)
    pid = str(product_id)
    if pid not in cart:
        return
    if quantity <= 0:
        del cart[pid]
    else:
        cart[pid]['quantity'] = quantity
    save_cart(request, cart)


def remove_from_cart(request, product_id):
    """Remove product from cart."""
    cart = get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        save_cart(request, cart)


def get_cart_items(request):
    """
    Return list of dicts with product, quantity, price, line_total for template.
    """
    try:
        cart = get_cart(request)
        if not isinstance(cart, dict):
            return []
        items = []
        for pid, data in cart.items():
            try:
                product = Product.objects.get(pk=int(pid))
            except Exception:
                continue
            try:
                qty = int(data.get('quantity', 1)) if isinstance(data, dict) else 1
                price = float(data.get('price', product.price)) if isinstance(data, dict) else float(product.price)
                items.append({
                    'product': product,
                    'quantity': qty,
                    'price': price,
                    'line_total': round(qty * price, 2),
                })
            except Exception:
                continue
        return items
    except Exception:
        return []
