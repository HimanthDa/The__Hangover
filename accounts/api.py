"""
User profile API for cross-server session synchronization.
Stores and retrieves user data from persistent storage.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json


@login_required
@require_http_methods(["GET", "POST"])
def user_profile_api(request):
    """
    Get or update user profile data.
    Data is persisted in the database and accessible from any server.
    """
    user = request.user

    if request.method == 'GET':
        # Return user profile data
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_authenticated': user.is_authenticated,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
        return JsonResponse(profile_data, status=200)

    elif request.method == 'POST':
        # Update user profile data
        try:
            data = json.loads(request.body)
            
            # Only allow updating specific fields
            allowed_fields = ['email', 'first_name', 'last_name']
            
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


@login_required
def session_status(request):
    """
    Check if user session is active and synchronized across servers.
    """
    return JsonResponse({
        'status': 'active',
        'user': request.user.username,
        'session_key': request.session.session_key,
        'authenticated': request.user.is_authenticated,
    }, status=200)
