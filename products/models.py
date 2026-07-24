"""
Product and Category models for beverages.
Each drink has name, category, brand, price, description, ingredients, history, image, etc.
Wines include alcohol_percentage and country of origin.
"""

from django.db import models


class Category(models.Model):
    """Category of beverage: Cold Drink, Soft Drink, Wine."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    A beverage product (cold drink, soft drink, or wine).
    Includes all required fields: name, category, brand, price, description,
    ingredients, history, image, alcohol % (wines), country of origin.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    brand = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Volume (e.g. '500ml', '1L')
    volume = models.CharField(max_length=20, blank=True, default='')
    description = models.TextField()
    ingredients = models.TextField(help_text='List of ingredients, one per line or comma-separated')
    history = models.TextField(help_text='History and origin of this drink')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    # For wines
    alcohol_percentage = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text='Alcohol by volume (e.g. 12.5 for wines)'
    )
    country_of_origin = models.CharField(max_length=100, blank=True)
    # Listing
    featured = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} ({self.brand})'

    @property
    def is_wine(self):
        return self.category.slug == 'wines'

    @property
    def image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass

        from django.templatetags.static import static

        static_map = {
            'iced-green-tea': 'products/Iced Green Tea.jpg',
            'sparkling-lemonade': 'products/Sparkling Lemonade.jpg',
            'iced-black-coffee': 'products/Iced Black Coffee.jpg',
            'lemon-iced-tea': 'products/Lemon Iced Tea.jpg',
            'mint-lime-cooler': 'products/Mint Lime Cooler.jpg',
            'berry-smoothie': 'products/Berry Smoothie.webp',
            'watermelon-juice': 'products/Watermelon Juice.jpg',
            'mango-lassi': 'products/Mango Lassi.jpg',
            'coconut-water': 'products/Coconut Water.webp',
            'cold-brew-coffee': 'products/Cold Brew Coffee.jpg',
            'classic-cola': 'products/Classic Cola.webp',
            'orange-soda': 'products/Orange Soda.jpg',
            'ginger-ale': 'products/Ginger Ale.webp',
            'diet-cola': 'products/Diet Cola.jpg',
            'lemon-lime-soda': 'products/Lemon-Lime Soda.jpg',
            'grape-soda': 'products/Grape Soda.jpg',
            'root-beer': 'products/Root Beer.jpg',
            'tonic-water': 'products/Tonic Water.jpg',
            'energy-drink-classic': 'products/Energy Drink Classic.jpg',
            'club-soda': 'products/Club Soda.jpg',
            'cabernet-sauvignon-reserve': 'products/Cabernet Sauvignon.webp',
            'chardonnay-oaked': 'products/Chardonnay.jpg',
            'rose-provence': 'products/Rosé.jpg',
            'prosecco-sparkling': 'products/Prosecco.webp',
            'pinot-noir': 'products/Pinot Noir.jpg',
            'sauvignon-blanc': 'products/Sauvignon Blanc.jpg',
            'riesling': 'products/Riesling.jpg',
            'malbec-reserva': 'products/Malbec.jpg',
            'champagne-brut': 'products/Champagne Brut.jpg',
            'ruby-port': 'products/Port Wine.webp',
            'green-tea-matcha': 'products/Green Tea.jpg',
            'black-tea-assam': 'products/Black Tea Assam.jpg',
            'black-tea-darjeeling': 'products/Black Tea Darjeeling.jpg',
            'earl-grey-black-tea': 'products/Earl Grey.jpg',
            'oolong-tea': 'products/Oolong Tea.jpg',
            'white-tea': 'products/White Tea.jpg',
            'herbal-tea-chamomile': 'products/Herbal Tea Chamomile.jpg',
            'herbal-tea-peppermint': 'products/Herbal Tea Peppermint.jpg',
            'puerh-tea': 'products/Pu\'erh Tea.jpg',
            'arabica-coffee': 'products/Arabica Coffee.jpg',
            'robusta-coffee': 'products/Robusta Coffee.jpg',
            'espresso-blend': 'products/Espresso.jpg',
            'cold-brew-premium': 'products/Cold Brew Coffee Premium.jpg',
            'turkish-coffee': 'products/Turkish Coffee.jpg',
        }
        rel_path = static_map.get(self.slug)
        if rel_path:
            return static(rel_path)
        return ''

