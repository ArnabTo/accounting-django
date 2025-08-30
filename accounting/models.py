from django.db import models
from django.utils import timezone

# Create your models here.
class AccountName(models.Model):
    name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Account(models.Model):
    # Define choices for account_type and detail_type
    ACCOUNT_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    DETAIL_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='debit', null=True, blank=True)
    detail_type = models.CharField(max_length=10, choices=DETAIL_TYPE_CHOICES, default='income', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    parent_account = models.ForeignKey(AccountName, on_delete=models.CASCADE, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    as_of = models.DateField(default=timezone.now, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    bank_routing = models.CharField(max_length=255, null=True, blank=True)
    bank_address = models.CharField(max_length=255, null=True, blank=True)
    
    # Add created_at and updated_at fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField( default=timezone.now)

    def __str__(self):
        return self.name