"""
Custom authentication backend allowing login with Username or Email address (case-insensitive).
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticate against User using username OR email address, case-insensitively.
    Strips leading and trailing whitespace automatically.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        clean_username = username.strip()

        # Try to find user by username or email (case-insensitive)
        user = User.objects.filter(
            Q(username__iexact=clean_username) | Q(email__iexact=clean_username)
        ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
