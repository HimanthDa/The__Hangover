"""
Middleware to enforce age verification for wine products and categories.
Redirects unverified users trying to access wine routes directly.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from urllib.parse import quote


class AgeGateMiddleware:
    """
    Backend protection ensuring users cannot bypass age verification
    by navigating directly to wine category or product URLs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.lower()
        
        # Check all possible wine route patterns
        is_wine_route = (
            '/category/wines' in path
            or '/category/wine' in path
            or '/products/wines' in path
            or '/products/wine' in path
            or path.endswith('/wines/')
            or path.endswith('/wines')
        )

        if is_wine_route:
            is_verified = (
                request.session.get('age_verified') is True
                or request.COOKIES.get('age_verified') == 'true'
                or (
                    request.user.is_authenticated
                    and hasattr(request.user, 'customerprofile')
                    and request.user.customerprofile.is_adult
                )
            )

            if not is_verified:
                messages.warning(
                    request,
                    'You must be at least 18 years old to enter the Wines section.'
                )
                home_url = reverse('main:home')
                return redirect(f"{home_url}?age_gate=wines&next={quote(request.path)}")

        return self.get_response(request)
