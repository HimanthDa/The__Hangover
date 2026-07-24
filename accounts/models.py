"""
Models for accounts app: Saved payment cards and customer profiles.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


def calculate_age(date_of_birth, today=None):
    """Calculate a full-year age from a date of birth."""
    if not date_of_birth:
        return None
    today = today or timezone.localdate()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age


class CustomerProfile(models.Model):
    """Extra customer details used for age-restricted products."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} profile'

    @property
    def age(self):
        return calculate_age(self.date_of_birth)

    @property
    def is_adult(self):
        age = self.age
        return age is not None and age >= 18


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
