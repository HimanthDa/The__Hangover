"""
Set volume values for existing products:
- Soft drinks category slug: 'soft-drinks' -> '500ml'
- Cold drinks category slug: 'cold-drinks' -> '500ml'
- Tea category slug: 'tea' -> '50ml'
- Coffee category slug: 'coffee' -> '50ml'
- Wines category slug: 'wines' -> '1L'

Run with project venv python:
& "c:\\Drinks and Wins\\venv\\Scripts\\python.exe" set_volumes.py
"""
import os
from pathlib import Path
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product, Category


soft_slug = 'soft-drinks'
cold_slug = 'cold-drinks'
tea_slug = 'tea'
coffee_slug = 'coffee'
wine_slug = 'wines'

soft_count = 0
cold_count = 0
tea_count = 0
coffee_count = 0
wine_count = 0
other = 0

try:
    soft_cat = Category.objects.get(slug=soft_slug)
except Category.DoesNotExist:
    soft_cat = None

try:
    cold_cat = Category.objects.get(slug=cold_slug)
except Category.DoesNotExist:
    cold_cat = None

try:
    tea_cat = Category.objects.get(slug=tea_slug)
except Category.DoesNotExist:
    tea_cat = None

try:
    coffee_cat = Category.objects.get(slug=coffee_slug)
except Category.DoesNotExist:
    coffee_cat = None

try:
    wine_cat = Category.objects.get(slug=wine_slug)
except Category.DoesNotExist:
    wine_cat = None

for p in Product.objects.all():
    if cold_cat and p.category_id == cold_cat.id:
        # cold drinks get 500ml as well
        p.volume = '500ml'
        p.save(update_fields=['volume'])
        cold_count += 1
    elif soft_cat and p.category_id == soft_cat.id:
        p.volume = '500ml'
        p.save(update_fields=['volume'])
        soft_count += 1
    elif tea_cat and p.category_id == tea_cat.id:
        p.volume = '50ml'
        p.save(update_fields=['volume'])
        tea_count += 1
    elif coffee_cat and p.category_id == coffee_cat.id:
        p.volume = '50ml'
        p.save(update_fields=['volume'])
        coffee_count += 1
    elif wine_cat and p.category_id == wine_cat.id:
        p.volume = '1L'
        p.save(update_fields=['volume'])
        wine_count += 1
    else:
        other += 1

print(f'Updated volumes: cold drinks={cold_count}, soft drinks={soft_count}, tea={tea_count}, coffee={coffee_count}, wines={wine_count}, others={other}')
