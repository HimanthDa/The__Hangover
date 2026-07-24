from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='confirmation'),
    path('history/', views.order_history, name='history'),
    path('order/<int:order_id>/', views.order_detail, name='detail'),
    path('receipt/<int:order_id>/', views.receipt, name='receipt'),
    path('receipt/<int:order_id>/pdf/', views.receipt_pdf, name='receipt_pdf'),
]
