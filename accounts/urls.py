from django.urls import path
from . import views
from . import api

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API endpoints for cross-server session sync
    path('api/profile/', api.user_profile_api, name='api_profile'),
    path('api/session-status/', api.session_status, name='api_session_status'),
]
