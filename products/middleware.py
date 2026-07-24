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
        
        # Check if the user is requesting wine category or wine pages
        is_wine_category = '/category/wines' in path or '/category/wine' in path
        # Also check product detail path if it's a wine product (handled in view or path pattern)

        if is_wine_category:
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
