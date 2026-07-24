"""
User authentication: login, signup, logout.
Card history and staff admin dashboard.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.db.models import Q
from django.utils.dateparse import parse_date
from products.models import Product, Category
from orders.models import Order
from .models import CustomerProfile, SavedCard

User = get_user_model()


def signup_view(request):
    """User registration with username, email, and password."""
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        date_of_birth_raw = request.POST.get('date_of_birth', '').strip()
        password = request.POST.get('password1', '')
        password_confirm = request.POST.get('password2', '')

        errors = []
        date_of_birth = parse_date(date_of_birth_raw) if date_of_birth_raw else None
        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username__iexact=username).exists():
            errors.append('Username is already taken.')

        if email and User.objects.filter(email__iexact=email).exists():
            errors.append('An account with this email already exists.')

        if not date_of_birth:
            errors.append('Date of birth is required.')

        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        elif password != password_confirm:
            errors.append('Passwords do not match.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/signup.html', {
                'username': username,
                'email': email,
                'date_of_birth': date_of_birth_raw,
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        CustomerProfile.objects.create(user=user, date_of_birth=date_of_birth)

        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user:
            login(request, authenticated_user)

        messages.success(request, f'Welcome to The Hangover, {user.username}! Your account has been created.')
        return redirect('main:home')

    return render(request, 'accounts/signup.html')


def login_view(request):
    """User login supporting Username or Email (case-insensitive & space-trimmed)."""
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not login_input or not password:
            messages.error(request, 'Please enter both username/email and password.')
            return render(request, 'accounts/login.html', {'login_input': login_input})

        user = authenticate(request, username=login_input, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'main:home'
            if next_url.startswith('/'):
                return redirect(next_url)
            return redirect('main:home')
        else:
            messages.error(request, 'Invalid username/email or password. Please check your credentials and try again.')
            return render(request, 'accounts/login.html', {'login_input': login_input})

    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out safely.')
    return redirect('main:home')


@login_required(login_url='accounts:login')
def card_history_view(request):
    """Display saved payment cards and payment method history for customer."""
    saved_cards = SavedCard.objects.filter(user=request.user)
    card_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'accounts/card_history.html', {
        'saved_cards': saved_cards,
        'card_orders': card_orders,
    })


@login_required
def dashboard_view(request):
    """Admin dashboard for staff users."""
    if not request.user.is_staff:
        messages.warning(request, 'Access denied. Staff only.')
        return redirect('main:home')

    product_count = Product.objects.count()
    category_count = Category.objects.count()
    order_count = Order.objects.count()
    total_revenue = Order.objects.aggregate(s=Sum('total'))['s'] or 0
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    return render(request, 'accounts/dashboard.html', {
        'product_count': product_count,
        'category_count': category_count,
        'order_count': order_count,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    })
