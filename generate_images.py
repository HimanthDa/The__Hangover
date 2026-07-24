"""
Generate product images for cold drinks, soft drinks, and wines.
"""

import os
import django
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product

# Create media/products directory if it doesn't exist
media_dir = Path('static/products/')
media_dir.mkdir(parents=True, exist_ok=True)

# Define product colors and styles
product_styles = {
    'iced-green-tea': {'color': '#4CAF50', 'text_color': '#FFF'},
    'sparkling-lemonade': {'color': '#FFD700', 'text_color': '#333'},
    'classic-cola': {'color': '#8B0000', 'text_color': '#FFF'},
    'orange-soda': {'color': '#FF8C00', 'text_color': '#FFF'},
    'ginger-ale': {'color': '#DAA520', 'text_color': '#333'},
    'cabernet-sauvignon-reserve': {'color': '#722F37', 'text_color': '#FFF'},
    'chardonnay-oaked': {'color': '#F4D03F', 'text_color': '#333'},
    'rose-provence': {'color': '#FFB6C1', 'text_color': '#333'},
    'prosecco-sparkling': {'color': '#FFF8DC', 'text_color': '#333'},
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (200, 200, 200)  # Default gray

def create_product_image(product_name, slug, color, text_color):
    """Create a simple product image with product name."""
    # Convert hex colors to RGB
    bg_color = hex_to_rgb(color)
    text_rgb = hex_to_rgb(text_color)
    
    # Create image
    img = Image.new('RGB', (400, 500), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default
    try:
        font = ImageFont.truetype('arial.ttf', 40)
    except:
        font = ImageFont.load_default()
    
    # Draw bottle shape
    outline_color = (0, 0, 0) if sum(text_rgb) > 382 else (255, 255, 255)
    draw.rectangle([80, 150, 320, 450], outline=outline_color, width=3)
    draw.rectangle([120, 80, 280, 150], outline=outline_color, width=3)  # Bottle neck
    draw.ellipse([80, 140, 320, 160], outline=outline_color, width=3)  # Top
    
    # Add text
    try:
        text_bbox = draw.textbbox((0, 0), product_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (400 - text_width) // 2
    except:
        text_x = 50
    
    draw.text((text_x, 250), product_name, fill=outline_color, font=font)
    
    # Save image
    image_path = media_dir / f'{slug}.png'
    img.save(image_path)
    print(f'Created image: {image_path}')
    return f'products/{slug}.png'

# Get all products and create images
products = Product.objects.all()

for product in products:
    if product.slug in product_styles:
        style = product_styles[product.slug]
        color = style['color']
        text_color = style['text_color']
        
        # Create image
        image_filename = create_product_image(
            product.name, 
            product.slug, 
            color, 
            text_color
        )
        
        # Update product with image
        product.image = image_filename
        product.save()
        print(f'Updated {product.name} with image')

print('All product images created and linked!')
