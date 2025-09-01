from django.core.management.base import BaseCommand
from django.utils import timezone
from accounting.models import AccountName, Account, Party, Item
from decimal import Decimal
import random
from django.db import models


class Command(BaseCommand):
    help = "Seed the database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # --- AccountName ---
        account_names = ['Cash', 'Bank',
                         'Accounts Receivable', 'Accounts Payable']
        for name in account_names:
            AccountName.objects.get_or_create(name=name)
        self.stdout.write(f"Created {len(account_names)} AccountNames")

        # --- Account ---
        account_types = ['debit', 'credit']
        detail_types = ['income', 'expense']
        status_choices = ['active', 'inactive']

        for i in range(5):
            parent = random.choice(AccountName.objects.all())
            Account.objects.create(
                account_type=random.choice(account_types),
                detail_type=random.choice(detail_types),
                name=f"Account {i+1}",
                number=f"ACCT-{1000+i}",
                parent_account=parent,
                balance=Decimal(random.randint(1000, 10000)),
                as_of=timezone.now(),
                description=f"Sample description for account {i+1}",
                status=random.choice(status_choices),
                bank_name=f"Bank {i+1}",
                bank_account=f"{random.randint(10000000, 99999999)}",
                bank_routing=f"{random.randint(100000, 999999)}"
            )
        self.stdout.write("Created 5 Accounts")

        # --- Party ---
        party_types = ['customer', 'vendor', 'staff']
        for i in range(5):
            Party.objects.create(
                type=random.choice(party_types),
                name=f"Party {i+1}",
                email=f"party{i+1}@example.com",
                phone=f"+8801{random.randint(100000000, 999999999)}",
                address=f"Address {i+1}"
            )
        self.stdout.write("Created 5 Parties")

        # --- Item ---
        item_types = ['product', 'service']
        for i in range(5):
            Item.objects.create(
                type=random.choice(item_types),
                name=f"Item {i+1}",
                sku=f"SKU-{i+1}",
                description=f"Description for Item {i+1}",
                cost=Decimal(random.randint(50, 500)),
                price=Decimal(random.randint(500, 2000)),
                quantity=random.randint(1, 100),
                unit="pcs",
                category=f"Category {i+1}",
                manufacturer=f"Manufacturer {i+1}",
                location=f"Location {i+1}",
                min_quantity=random.randint(1, 10)
            )
        self.stdout.write("Created 5 Items")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
