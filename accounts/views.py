"""
User authentication: login, signup, logout.
Admin dashboard for staff users.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from products.models import Product, Category
from orders.models import Order


def signup_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('main:home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('main:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('main:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'main:home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('main:home')


@login_required
def dashboard_view(request):
    """
    Admin dashboard: only staff can access.
    Shows product count, order count, recent orders.
    """
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
