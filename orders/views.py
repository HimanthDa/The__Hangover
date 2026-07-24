"""
Checkout and order confirmation.
Demo payment: no real gateway, just create order and show confirmation.
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from .models import Order, OrderItem
from cart.utils import get_cart_items, save_cart, add_to_cart
from accounts.models import CustomerProfile, calculate_age
from django.template.loader import render_to_string
from django.http import HttpResponse

import logging

# helper for QR generation


def _user_can_view_order(user, order):
    """Return True when a user owns the order or is staff."""
    return user.is_authenticated and (order.user_id == user.id or user.is_staff)

def _get_last_address_data(request):
    default_data = {
        'email': '',
        'first_name': '',
        'last_name': '',
        'address': '',
        'city': '',
        'state': '',
        'postal_code': '',
        'country': 'INDIA',
        'phone': '',
    }

    saved_data = request.session.get('last_address', {})
    data = {**default_data, **saved_data}

    if request.user.is_authenticated:
        last_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        if last_order:
            data.update({
                'email': last_order.email,
                'first_name': last_order.first_name,
                'last_name': last_order.last_name,
                'address': last_order.address,
                'city': last_order.city,
                'state': last_order.state,
                'postal_code': last_order.postal_code,
                'country': last_order.country,
                'phone': last_order.phone,
            })

    return data


def _cart_contains_wine(items):
    return any(item['product'].is_wine for item in items)


def _known_underage_for_wine(user):
    if not user.is_authenticated:
        return False
    try:
        profile = user.customer_profile
    except CustomerProfile.DoesNotExist:
        return False
    return profile.date_of_birth and not profile.is_adult


def _get_saved_date_of_birth(request):
    if request.user.is_authenticated:
        try:
            return request.user.customer_profile.date_of_birth
        except CustomerProfile.DoesNotExist:
            return None

    date_of_birth_raw = request.session.get('date_of_birth')
    return parse_date(date_of_birth_raw) if date_of_birth_raw else None


def _checkout_context(items, subtotal, total, data, contains_wine, date_of_birth=''):
    return {
        'cart_items': items,
        'subtotal': subtotal,
        'total': total,
        'contains_wine': contains_wine,
        'date_of_birth': date_of_birth,
        **data,
    }


def _generate_qr_data_uri(amount):
    """Return a base64 data URI containing a QR code for the given amount.

    If the qrcode library is unavailable it returns ``None`` so templates can
    fall back to a static image file.
    """
    try:
        import io, base64
        import qrcode
    except ImportError:
        logging.getLogger(__name__).warning('qrcode library missing, using static QR image')
        return None
    payment_phone = '6303222193'
    # Use a UPI-style QR payload so payment apps can display the order amount automatically.
    qr_payload = (
        f"upi://pay?pa={payment_phone}@upi"
        f"&pn=DrinksAndWins"
        f"&am={amount:.2f}"
        f"&cu=INR"
        f"&tn=Order+Payment"
    )
    qr_img = qrcode.make(qr_payload)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{qr_b64}"


@require_http_methods(['GET', 'POST'])
def checkout(request):
    """
    Checkout page: show form and cart summary.
    On POST: create order, clear cart, redirect to confirmation.
    """
    try:
        items = get_cart_items(request)
    except Exception as e:
        logging.getLogger(__name__).error(f"Cart retrieval error: {e}")
        items = []

    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart')

    subtotal = sum(item['line_total'] for item in items)
    total = subtotal
    contains_wine = _cart_contains_wine(items)

    initial_data = _get_last_address_data(request)
    saved_date_of_birth = _get_saved_date_of_birth(request)
    initial_date_of_birth = saved_date_of_birth.isoformat() if saved_date_of_birth else ''

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', 'INDIA').strip()
        phone = request.POST.get('phone', '').strip()
        date_of_birth_raw = request.POST.get('date_of_birth', '').strip()
        posted_date_of_birth = parse_date(date_of_birth_raw) if date_of_birth_raw else None
        effective_date_of_birth = posted_date_of_birth or saved_date_of_birth

        form_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country': country,
            'phone': phone,
        }

        if not all([email, first_name, last_name, address, city, state, postal_code, country]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'orders/checkout.html', _checkout_context(
                items, subtotal, total, form_data, contains_wine, date_of_birth_raw
            ))

        if contains_wine:
            age = calculate_age(effective_date_of_birth)
            if age is None:
                messages.error(request, 'Date of birth is required to buy wine products.')
                return render(request, 'orders/checkout.html', _checkout_context(
                    items, subtotal, total, form_data, contains_wine, date_of_birth_raw
                ))
            if age < 18:
                messages.error(request, 'You must be 18 or older to buy wine products.')
                return render(request, 'orders/checkout.html', _checkout_context(
                    items, subtotal, total, form_data, contains_wine, date_of_birth_raw
                ))

        session_key = getattr(request.session, 'session_key', None) or 'guest'

        try:
            if effective_date_of_birth:
                if request.user.is_authenticated:
                    CustomerProfile.objects.update_or_create(
                        user=request.user,
                        defaults={'date_of_birth': effective_date_of_birth},
                    )
                else:
                    request.session['date_of_birth'] = effective_date_of_birth.isoformat()

            order = Order(
                user=request.user if request.user.is_authenticated else None,
                email=email,
                first_name=first_name,
                last_name=last_name,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                phone=phone,
                subtotal=Decimal(str(subtotal)),
                total=Decimal(str(total)),
                status='pending',
                payment_method='qr',
                payment_id=f'QR-{session_key}',
            )
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    quantity=item['quantity'],
                    price=Decimal(str(item['price'])),
                )

            try:
                request.session['last_address'] = {
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'address': address,
                    'city': city,
                    'state': state,
                    'postal_code': postal_code,
                    'country': country,
                    'phone': phone,
                }
            except Exception:
                pass

            # Clear cart
            save_cart(request, {})
            messages.success(request, 'Order placed successfully!')
            return redirect('orders:confirmation', order_id=order.id)

        except Exception as err:
            logging.getLogger(__name__).error(f"Checkout POST error: {err}")
            messages.error(request, f"There was an error placing your order ({err}). Please try again.")
            return render(request, 'orders/checkout.html', _checkout_context(
                items, subtotal, total, form_data, contains_wine, date_of_birth_raw
            ))

    return render(request, 'orders/checkout.html', _checkout_context(
        items, subtotal, total, initial_data, contains_wine, initial_date_of_birth
    ))


def order_confirmation(request, order_id):
    """Payment page after placing an order."""
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'confirmed':
        return redirect('orders:receipt', order_id=order.id)

    qr_data_uri = _generate_qr_data_uri(order.total)
    if request.method == 'POST':
        order.status = 'confirmed'
        order.save()
        return redirect('orders:receipt', order_id=order.id)

    return render(request, 'orders/confirmation.html', {
        'order': order,
        'qr_data_uri': qr_data_uri,
    })


def receipt(request, order_id):
    """HTML receipt page (printable)."""
    order = get_object_or_404(Order, id=order_id)
    # ensure logged in user matches order if order belongs to a user
    if order.user_id and request.user.is_authenticated:
        if order.user_id != request.user.id and not request.user.is_staff:
            return redirect('main:home')
    elif order.user_id and not request.user.is_authenticated:
        return redirect('accounts:login')

    if order.status != 'confirmed':
        return redirect('orders:confirmation', order_id=order.id)
    qr_data_uri = _generate_qr_data_uri(order.total)
    return render(request, 'orders/receipt.html', {'order': order, 'qr_data_uri': qr_data_uri})


def receipt_pdf(request, order_id):
    """Render and return PDF of receipt when possible."""
    order = get_object_or_404(Order, id=order_id)
    if order.user_id and request.user.is_authenticated:
        if order.user_id != request.user.id and not request.user.is_staff:
            return redirect('main:home')
    elif order.user_id and not request.user.is_authenticated:
        return redirect('accounts:login')

    qr_data_uri = _generate_qr_data_uri(order.total)
    html = render_to_string('orders/receipt.html', {'order': order, 'qr_data_uri': qr_data_uri})

    try:
        from weasyprint import HTML
    except Exception:
        return HttpResponse(html, content_type='text/html')

    try:
        pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
    except Exception:
        return HttpResponse(html, content_type='text/html')

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt-{order.id}.pdf"'
    return response


def order_history(request):
    """List of user's orders (requires login)."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


def order_detail(request, order_id):
    """Single order detail (user's own or admin)."""
    order = get_object_or_404(Order, id=order_id)
    if not _user_can_view_order(request.user, order):
        if request.user.is_authenticated:
            messages.warning(request, 'You can only view your own orders.')
            return redirect('orders:history')
        return redirect('accounts:login')
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required(login_url='accounts:login')
@require_POST
def add_order_to_cart(request, order_id):
    """Add available items from a previous order back to the cart."""
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), id=order_id)
    if not _user_can_view_order(request.user, order):
        messages.warning(request, 'You can only reorder your own orders.')
        return redirect('orders:history')

    added_count = 0
    skipped_count = 0
    for item in order.items.all():
        if item.product and item.product.is_wine and _known_underage_for_wine(request.user):
            skipped_count += item.quantity
            continue

        if item.product and item.product.in_stock:
            if add_to_cart(request, item.product.id, item.quantity):
                added_count += item.quantity
            else:
                skipped_count += item.quantity
        else:
            skipped_count += item.quantity

    if added_count:
        messages.success(request, f'Added {added_count} item(s) from order #{order.id} to your cart.')
    if skipped_count:
        messages.warning(request, f'{skipped_count} item(s) from that order are no longer available.')
    if not added_count and not skipped_count:
        messages.info(request, 'That order has no items to add.')

    return redirect('cart:cart')
