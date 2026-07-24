from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.cart_add, name='add'),
    path('update/<int:product_id>/', views.cart_update, name='update'),
    path('remove/<int:product_id>/', views.cart_remove, name='remove'),
    path('history/', views.cart_history_view, name='history'),
    path('history/readd/<int:history_id>/', views.cart_history_readd, name='history_readd'),
]
