"""
Assign uploaded product images to Product.image fields.
Run: c:/Drinks and Wins/venv/Scripts/python.exe assign_images.py
"""
import os
from pathlib import Path
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product
media_dir = Path('static/products')
if not media_dir.exists():
    print(f"Media folder not found: {media_dir.resolve()}")
    raise SystemExit(1)

from unicodedata import normalize

files = list(media_dir.iterdir())
files_lower = {f.name.lower(): f for f in files}

def normalize_text(s: str) -> str:
    s = normalize('NFKD', s)
    return ''.join(ch for ch in s if ord(ch) < 128).lower()

updated = []
missing = []

for product in Product.objects.all():
    found = None
    # exact slug match first
    for f in files:
        name_lower = f.name.lower()
        if product.slug in name_lower:
            found = f
            break

    # then try matching by product name words (tolerant to spaces/case/accents)
    if not found:
        target = normalize_text(product.name)
        for f in files:
            fname_norm = normalize_text(f.stem)
            # check if all words of target appear in filename stem
            words = [w for w in target.split() if w]
            if all(word in fname_norm for word in words):
                found = f
                break

    if found:
        rel_path = f"products/{found.name}"
        product.image = rel_path
        product.save(update_fields=['image'])
        updated.append((product.slug, rel_path))
        print(f"Updated {product.slug} -> {rel_path}")
    else:
        missing.append(product.slug)

print('\nSummary:')
print(f'Updated {len(updated)} products')
if missing:
    print(f'Missing images for {len(missing)} products: {missing}')
else:
    print('All products have images')
