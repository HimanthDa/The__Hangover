from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('verify-age/', views.verify_age, name='verify_age'),
    path('category/<slug:category_slug>/', views.product_list, name='list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='detail'),
]
