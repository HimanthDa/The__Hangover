from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('drinks-and-wins-history/', views.site_history, name='site_history'),
    path('drink-history/', views.drink_history, name='drink_history'),
    path('wine-history/', views.wine_history, name='wine_history'),
]
