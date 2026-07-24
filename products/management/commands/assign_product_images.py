"""
Assign images from static/products/ to products.
Copies files to media/products/ and sets Product.image.
Run: python manage.py assign_product_images
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from products.models import Product


# Map static filename (without extension) to product name in DB (for fuzzy match)
NAME_ALIASES = {
    'rose': 'Rosé',
    'rosé': 'Rosé',
}


def normalize_name(s):
    """Lowercase, strip, for matching."""
    return (s or '').lower().strip()


def find_product_for_filename(name_without_ext):
    """Find a Product that matches this image filename."""
    name_lower = normalize_name(name_without_ext)
    # Try alias first (e.g. "rose" -> product name "Rosé")
    if name_lower in NAME_ALIASES:
        product_name = NAME_ALIASES[name_lower]
        try:
            return Product.objects.get(name=product_name)
        except Product.DoesNotExist:
            pass
    # Try exact match on product name (case-insensitive)
    for p in Product.objects.all():
        if normalize_name(p.name) == name_lower:
            return p
    # Try slug (filename "cabernet-sauvignon" or "Cabernet Sauvignon" -> slug cabernet-sauvignon-reserve)
    slug_base = name_lower.replace(' ', '-')
    for p in Product.objects.all():
        if p.slug.startswith(slug_base) or slug_base in p.slug:
            return p
    return None


class Command(BaseCommand):
    help = 'Copy images from static/products/ to media/products/ and assign to products.'

    def handle(self, *args, **options):
        static_products = Path(settings.BASE_DIR) / 'static' / 'products'
        media_products = Path(settings.MEDIA_ROOT) / 'products'
        if not static_products.exists():
            self.stdout.write(self.style.WARNING(f'Directory not found: {static_products}'))
            return

        media_products.mkdir(parents=True, exist_ok=True)
        extensions = {'.webp', '.jpg', '.jpeg', '.png'}
        assigned = 0

        for path in sorted(static_products.iterdir()):
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            name_without_ext = path.stem
            product = find_product_for_filename(name_without_ext)
            if not product:
                self.stdout.write(self.style.WARNING(f'No product matched for image: {path.name}'))
                continue
            # Copy to media/products/<slug><suffix>
            safe_name = f'{product.slug}{path.suffix}'
            dest = media_products / safe_name
            shutil.copy2(path, dest)
            # Set product image path (relative to MEDIA_ROOT)
            product.image = f'products/{safe_name}'
            product.save()
            assigned += 1
            self.stdout.write(f'  Assigned {path.name} -> {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Assigned {assigned} images to products.'))
