# Use Django's default User admin
from django.contrib import admin

from .models import CustomerProfile, SavedCard


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'age', 'is_adult')
    search_fields = ('user__username', 'user__email')


@admin.register(SavedCard)
class SavedCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_brand', 'last_four', 'cardholder_name', 'last_used')
    search_fields = ('user__username', 'cardholder_name', 'last_four')
