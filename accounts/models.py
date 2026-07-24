"""
Models for accounts app: Saved payment cards and customer profiles.
"""

from django.db import models
from django.conf import settings


class SavedCard(models.Model):
    """
    Saved payment cards / card history for customer orders.
    """
    CARD_BRAND_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('rupay', 'RuPay'),
        ('amex', 'American Express'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_cards'
    )
    cardholder_name = models.CharField(max_length=100)
    card_brand = models.CharField(max_length=30, choices=CARD_BRAND_CHOICES, default='visa')
    last_four = models.CharField(max_length=4)
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_used']

    def __str__(self):
        return f"{self.get_card_brand_display()} ending in {self.last_four} ({self.cardholder_name})"
