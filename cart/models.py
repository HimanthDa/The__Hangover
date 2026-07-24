"""
Cart models: CartHistory stores items added to cart by authenticated users.
"""

from django.db import models
from django.conf import settings
from products.models import Product


class CartHistory(models.Model):
    """
    Tracks products added to cart by registered users over time.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_history'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_history_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'Cart histories'

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity} ({self.updated_at.date()})"

    @property
    def line_total(self):
        return self.quantity * self.price
