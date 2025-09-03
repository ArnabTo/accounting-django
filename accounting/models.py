from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver



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

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    account_type = models.CharField(
        max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='debit', null=True, blank=True)
    detail_type = models.CharField(
        max_length=10, choices=DETAIL_TYPE_CHOICES, default='income', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    parent_account = models.ForeignKey(
        AccountName, on_delete=models.CASCADE, null=True, blank=True)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    as_of = models.DateTimeField(default=timezone.now, blank=True)
    description = models.TextField(blank=True, null=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    bank_routing = models.CharField(max_length=255, null=True, blank=True)
    bank_address = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, null=True, blank=True)
    # Add created_at and updated_at fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

# Shared models: Parties (Customers/Vendors), Items


class Party(models.Model):  # For Customers, Vendors, Staff, etc.
    PARTY_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('staff', 'Staff'),
    ]
    type = models.CharField(
        max_length=50, choices=PARTY_TYPE_CHOICES, default='customer')
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Item(models.Model):  # For products/services in sales, purchases, inventory, bills
    ITEM_TYPE_CHOICES = [
        ('product', 'Product'),
        ('service', 'Service'),
    ]
    type = models.CharField(
        max_length=50, choices=ITEM_TYPE_CHOICES, default='product')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(default=0)  # For inventory tracking
    unit = models.CharField(max_length=50, null=True,
                            blank=True)  # e.g., pcs, kg
    category = models.CharField(max_length=255, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    min_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

# Banking Feeds: Bank Transactions/Statements


class BankTransaction(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField(default=timezone.now)
    payee = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    withdrawal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Could be FK to a Rule model if needed
    banking_rule = models.CharField(max_length=255, null=True, blank=True)
    cleared = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transaction {self.date} for {self.account}"

# Transactions: Sales


class SalesPayment(models.Model):
    date = models.DateField(default=timezone.now)

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)  # e.g., cash, card
    in_words = models.CharField(max_length=255, null=True, blank=True)
    bank = models.CharField(max_length=255, null=True, blank=True)
    branch = models.CharField(max_length=255, null=True, blank=True)

    # Asset against payment
    against = models.CharField(max_length=255, null=True, blank=True)
    plot_no = models.CharField(max_length=255, null=True, blank=True)
    road_no = models.CharField(max_length=255, null=True, blank=True)
    block = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    project = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    invoice = models.ForeignKey(
        'SalesInvoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    status = models.CharField(max_length=50, default='paid')

    # Placeholder for integration/mapping
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    name_of_purchaser = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class SalesInvoice(models.Model):
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'customer'})
    status = models.CharField(max_length=50, default='open')
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    items = models.ManyToManyField(
        Item, through='InvoiceItem')  # For line items
    debit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='debit_invoices')
    credit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_invoices')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Invoice {self.id} for {self.customer.name}"


# Intermediate for line items in invoices/bills/etc.
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class SalesOrderReturn(models.Model):
    order_number = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    customer = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'customer'})
    payment_mode = models.CharField(max_length=50)
    channel = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class SalesRefund(models.Model):
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    order_number = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

# Transactions: Expenses


class Expense(models.Model):
    attach_receipt = models.FileField(upload_to='expenses/', null=True, blank=True)
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, blank=True, null=True, related_name='vendor_expenses')
    name = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    expense_category = models.CharField(max_length=255, blank=True, null=True)
    expense_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(
        Party, on_delete=models.CASCADE, blank=True, null=True, related_name='customer_expenses')
    # Advance options
    currency = models.CharField(max_length=3, default='USD')
    tax1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_mode = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
    ], default='cash')
    reference = models.CharField(max_length=255, blank=True, null=True)
    repeat_every = models.CharField(max_length=50, blank=True, null=True, default='1 week')

    def __str__(self):
        return f"Expense {self.name} - {self.amount}"

# Transactions: Payslips (Payroll)


class Payslip(models.Model):
    name = models.CharField(max_length=255)
    template = models.CharField(max_length=255, null=True, blank=True)
    month = models.CharField(max_length=50)  # e.g., 'August 2025'
    staff = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'staff'})
    created_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

# Transactions: Purchases (Similar to Sales but for vendors)


class PurchaseOrder(models.Model):
    order_date = models.DateField(default=timezone.now)
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'vendor'})
    po_value = models.DecimalField(max_digits=10, decimal_places=2)
    tax_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_including_tax = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    items = models.ManyToManyField(Item, through='PurchaseOrderItem')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


# Could be merged with Bill, but kept separate per description
class PurchaseInvoice(models.Model):
    invoice_no = models.CharField(max_length=100)
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'vendor'})
    contract = models.CharField(max_length=255, null=True, blank=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateField(default=timezone.now)
    recurring_from = models.DateField(null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_including_tax = models.DecimalField(max_digits=10, decimal_places=2)
    payment_request_status = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class PurchasePayment(models.Model):
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class PurchaseOrderReturn(models.Model):
    return_number = models.CharField(max_length=100)
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'vendor'})
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_after_discount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateField(default=timezone.now)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class PurchaseRefund(models.Model):
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    purchase_order_return = models.ForeignKey(
        PurchaseOrderReturn, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

# Transactions: Inventory


class InventoryReceivingVoucher(models.Model):
    delivery_docket_code = models.CharField(max_length=100)
    accounting_date = models.DateField(default=timezone.now)
    total_tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_goods_value = models.DecimalField(max_digits=10, decimal_places=2)
    value_of_inventory = models.DecimalField(max_digits=10, decimal_places=2)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    # Add through model if quantities needed
    items = models.ManyToManyField(Item)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class StockExport(models.Model):
    inventory_delivery_voucher_code = models.CharField(max_length=100)
    customer = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'customer'})
    accounting_date = models.DateField(default=timezone.now)
    invoices = models.ManyToManyField(SalesInvoice, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class LossAdjustment(models.Model):
    type = models.CharField(max_length=50)  # lost or adjusted
    time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    items = models.ManyToManyField(Item)  # With quantities if needed
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class OpeningStock(models.Model):
    commodity_code = models.CharField(max_length=100)
    commodity_name = models.CharField(max_length=255)
    sku_code = models.CharField(max_length=100)
    opening_stock = models.IntegerField()
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

# Transactions: Manufacturing


class ManufacturingOrder(models.Model):
    reference = models.CharField(max_length=100)
    product = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='manufactured_product')
    bill_of_material = models.TextField(
        null=True, blank=True)  # Or M2M to components
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    routing = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

# Transactions: Fixed Equipment (Assets, etc.)


class Asset(models.Model):
    serial_number = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='assets/', null=True, blank=True)
    model = models.CharField(max_length=255)
    model_no = models.CharField(max_length=100)
    category = models.CharField(max_length=255)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class License(models.Model):
    product_key = models.CharField(max_length=255)
    expiration_date = models.DateField(null=True, blank=True)
    licensed_to_email = models.EmailField()
    licensed_to_name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    total = models.IntegerField()  # e.g., number of licenses
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Component(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100)
    category = models.CharField(max_length=255)
    total = models.IntegerField()
    remaining = models.IntegerField()
    min_quantity = models.IntegerField()
    location = models.CharField(max_length=255)
    order_number = models.CharField(max_length=100)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Consumable(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='consumables/', null=True, blank=True)
    category = models.CharField(max_length=255)
    model_no = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    total = models.IntegerField()
    min_quantity = models.IntegerField()
    avail = models.IntegerField()  # Available
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Maintenance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    maintenance_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Depreciation(models.Model):
    serial_number = models.CharField(max_length=100)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

# Bills (Vendor Bills, similar to PurchaseInvoice but separate per description)


class Bill(models.Model):
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'vendor'})
    bill_date = models.DateField(default=timezone.now)
    name = models.CharField(max_length=255, null=True, blank=True)  # Optional
    reference = models.CharField(max_length=100)
    memo = models.TextField(null=True, blank=True)
    due_date = models.DateField()
    attachment = models.FileField(upload_to='bills/', null=True, blank=True)
    debit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='debit_bills')
    credit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='open')
    items = models.ManyToManyField(
        Item, through='BillItem')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    # Or description for expenses
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

# Checks


class Check(models.Model):
    bank_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, limit_choices_to={'bank_name__isnull': False})
    check_number = models.CharField(max_length=50)
    pay_to = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    memo = models.TextField(null=True, blank=True)
    sign = models.CharField(max_length=255, null=True,
                            blank=True)  # Signature field?
    date = models.DateField(default=timezone.now)
    vendor = models.ForeignKey(Party, on_delete=models.SET_NULL,
                               null=True, blank=True, limit_choices_to={'type': 'vendor'})
    status = models.CharField(max_length=50, default='issued')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

# Journal Entry (General ledger entries, connecting to accounts)


class JournalEntry(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(null=True, blank=True)



# Reconciliation Models
class ReconcileStatement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    beginning_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ending_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # If this is a new record (no ID yet)
        if not self.pk:
            # Get the most recent statement for this account
            previous_statement = ReconcileStatement.objects.filter(
                account=self.account,
                ending_date__lt=self.ending_date
            ).order_by('-ending_date').first()
            
            # Set beginning balance to previous statement's ending balance
            if previous_statement:
                self.beginning_balance = previous_statement.ending_balance
            else:
                self.beginning_balance = 0
                
        super().save(*args, **kwargs)
    
    @property
    def cleared_balance(self):
        """Calculate cleared balance: beginning_balance - payments + deposits"""
        cleared_transactions = self.transactions.filter(is_cleared=True)
        total_payments = cleared_transactions.aggregate(
            total=models.Sum('payment_amount')
        )['total'] or 0
        total_deposits = cleared_transactions.aggregate(
            total=models.Sum('deposit_amount')
        )['total'] or 0
        return self.beginning_balance - total_payments + total_deposits
    
    @property
    def total_payments(self):
        """Get total cleared payments"""
        cleared_transactions = self.transactions.filter(is_cleared=True)
        total = cleared_transactions.aggregate(
            total=models.Sum('payment_amount')
        )['total']
        return total if total is not None else 0
    
    @property
    def total_deposits(self):
        """Get total cleared deposits"""
        cleared_transactions = self.transactions.filter(is_cleared=True)
        total = cleared_transactions.aggregate(
            total=models.Sum('deposit_amount')
        )['total']
        return total if total is not None else 0
    
    def calculate_difference(self):
        """Calculate difference between ending balance and cleared balance"""
        return self.ending_balance - self.cleared_balance
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Check if there's a related reconciliation
        try:
            reconciliation = self.reconciliation
            difference = self.calculate_difference()
            # If difference is 0, update reconciliation status
            if abs(difference) < 0.01:  # Using small threshold for floating point comparison
                if reconciliation.status != 'completed':
                    reconciliation.status = 'completed'
                    reconciliation.save(update_fields=['status'])
            else:
                if reconciliation.status != 'pending':
                    reconciliation.status = 'pending'
                    reconciliation.save(update_fields=['status'])
        except Reconciliation.DoesNotExist:
            pass  # No reconciliation exists yet
    
    def __str__(self):
        return f"Statement for {self.account} - {self.ending_date}"

class ReconcileTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('cheque_expense', 'Cheque Expense'),
    ]
    
    statement = models.ForeignKey(ReconcileStatement, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    date = models.DateField(default=timezone.now)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='deposit')
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    payee = models.ForeignKey('Party', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_cleared = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.date} - {self.description}"
    
    @receiver(pre_save, sender='accounting.ReconcileTransaction')
    def capture_old_values(sender, instance, **kwargs):
        """Store old values before save to calculate the difference"""
        if instance.pk:  # If this is an update
            try:
                old = sender.objects.get(pk=instance.pk)
                instance._old_payment = old.payment_amount
                instance._old_deposit = old.deposit_amount
                instance._old_cleared = old.is_cleared
            except sender.DoesNotExist:
                instance._old_payment = 0
                instance._old_deposit = 0
                instance._old_cleared = False
        else:  # If this is a new instance
            instance._old_payment = 0
            instance._old_deposit = 0
            instance._old_cleared = False

    @receiver(post_save, sender='accounting.ReconcileTransaction')
    def update_statement(sender, instance, created, **kwargs):
        """Update the related ReconcileStatement's computed values"""
        if instance.statement:
            # Force refresh the cached properties by saving the statement
            instance.statement.save()
            
            # Refresh from db to ensure we have latest values
            instance.statement.refresh_from_db()

    @receiver(pre_delete, sender='accounting.ReconcileTransaction')
    def handle_delete(sender, instance, **kwargs):
        """Handle updates when a transaction is deleted"""
        if instance.statement:
            # Save the statement to trigger recalculation of properties
            instance.statement.save()

class Reconciliation(models.Model):
    RECONCILIATION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('discrepancy', 'Has Discrepancy')
    ]
    
    statement = models.OneToOneField(ReconcileStatement, on_delete=models.CASCADE, related_name='reconciliation')
    reconciled_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=RECONCILIATION_STATUS, default='pending')
    adjustment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        if self.statement:
            difference = self.statement.calculate_difference()
            # If difference is 0, mark as completed
            if abs(difference) < 0.01:  # Using small threshold for floating point comparison
                self.status = 'completed'
            else:
                self.status = 'pending'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Reconciliation for {self.statement} - {self.status}"
    
