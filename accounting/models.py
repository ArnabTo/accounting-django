from django.db import models
from django.utils import timezone

# Create your models here.


class AccountName(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class Account(models.Model):
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
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

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
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

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
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, null=True,
                            blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    min_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.name

# Banking Feeds: Bank Transactions/Statements


class BankTransaction(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField(default=timezone.now)
    payee = models.ForeignKey(
        Party, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    withdrawal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    banking_rule = models.CharField(max_length=255, null=True, blank=True)
    cleared = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.date} for {self.account}"

# Transactions: Sales

# Orders


class Order(models.Model):
    PAYMENT_MODE = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ]

    order_number = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    seller = models.CharField(max_length=255, null=True, blank=True)
    order_date = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(
        max_length=50, choices=PAYMENT_MODE, default='cash')
    customer = models.ForeignKey(
        Party, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.order_number} ({self.customer})"

    # Calculate total automatically
    def calculate_total(self):
        total = sum(item.subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"


class SalesInvoice(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Party, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='open')
    debit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='debit_invoices')
    credit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_invoices')
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class SalesPayment(models.Model):
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    invoice = models.ForeignKey(
        'SalesInvoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    status = models.CharField(max_length=50, default='paid')
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class SalesOrderReturn(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='returns', null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    channel = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class SalesRefund(models.Model):
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    order_number = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

# Transactions: Expenses


class Expense(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255)
    payment_mode = models.CharField(max_length=50)
    invoice = models.FileField(upload_to='expenses/', null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

# Transactions: Payslips (Payroll)


class Payslip(models.Model):
    name = models.CharField(max_length=255)
    template = models.CharField(max_length=255, null=True, blank=True)
    month = models.CharField(max_length=50)
    staff = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'staff'})
    created_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

# Transactions: Purchases (Similar to Sales but for vendors)


class PurchaseOrder(models.Model):
    STATUS = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]
    PAYMENT_MODE = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ]
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    purchase_order = models.CharField(max_length=100, blank=True, null=True)
    po_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_including_tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, null=True, blank=True)
    order_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(
        max_length=50, choices=STATUS, default='unpaid')
    payment_request_status = models.CharField(
        max_length=50, choices=REQUEST_STATUS, default='pending')
    payment_mode = models.CharField(
        choices=PAYMENT_MODE, max_length=50, null=True, blank=True)
    expense_of = models.CharField(max_length=50, null=True, blank=True)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"Order {self.purchase_order} ({self.vendor})"

    def calculate_total(self):
        result = self.items.aggregate(
            subtotal=models.Sum(models.F('quantity') * models.F('unit_price')),
        )

        subtotal = result['subtotal'] or 0
        tax_amount = (subtotal * self.tax_value) / 100 if self.tax_value else 0
        total_with_tax = subtotal + tax_amount

        # Only update if values changed
        update_fields = []
        if self.po_value != subtotal:
            self.po_value = subtotal
            update_fields.append('po_value')
        if self.total_including_tax != total_with_tax:
            self.total_including_tax = total_with_tax
            update_fields.append('total_including_tax')

        if update_fields:
            self.save(update_fields=update_fields)

        return total_with_tax

    def save(self, *args, **kwargs):
        # Generate purchase order number if not provided
        if not self.purchase_order:
            self.purchase_order = self.generate_po_number()
        super().save(*args, **kwargs)

    def generate_po_number(self):
        from django.utils.timezone import now
        return f"PO-{now().strftime('%Y%m%d-%H%M%S')}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.item.name if self.item else 'No Item'} x {self.quantity}"

    def save(self, *args, **kwargs):
        # Set unit_price from item if not provided
        if self.item and not self.unit_price:
            self.unit_price = self.item.price
        super().save(*args, **kwargs)


# Transactions: Purchase Invoices

class PurchaseInvoice(models.Model):
    invoice_no = models.CharField(max_length=100, null=True, blank=True)
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'vendor'})
    contract = models.CharField(max_length=255, null=True, blank=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    recurring_from = models.DateTimeField(null=True, blank=True)
    invoice_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class PurchasePayment(models.Model):
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='not mapped')
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class PurchaseOrderReturn(models.Model):
    return_number = models.CharField(max_length=100)
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'vendor'})
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_after_discount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class PurchaseRefund(models.Model):
    date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    purchase_order_return = models.ForeignKey(
        PurchaseOrderReturn, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

# Transactions: Inventory


class InventoryReceivingVoucher(models.Model):
    delivery_docket_code = models.CharField(max_length=100)
    accounting_date = models.DateTimeField(default=timezone.now)
    total_tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_goods_value = models.DecimalField(max_digits=10, decimal_places=2)
    value_of_inventory = models.DecimalField(max_digits=10, decimal_places=2)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    # Add through model if quantities needed
    items = models.ManyToManyField(Item)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class StockExport(models.Model):
    inventory_delivery_voucher_code = models.CharField(max_length=100)
    customer = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'customer'})
    accounting_date = models.DateTimeField(default=timezone.now)
    invoices = models.ManyToManyField(SalesInvoice, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class LossAdjustment(models.Model):
    type = models.CharField(max_length=50)
    time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    items = models.ManyToManyField(Item)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class OpeningStock(models.Model):
    commodity_code = models.CharField(max_length=100)
    commodity_name = models.CharField(max_length=255)
    sku_code = models.CharField(max_length=100)
    opening_stock = models.IntegerField()
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

# Transactions: Manufacturing


class ManufacturingOrder(models.Model):
    reference = models.CharField(max_length=100)
    product = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='manufactured_product')
    bill_of_material = models.TextField(
        null=True, blank=True)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    routing = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

# Transactions: Fixed Equipment (Assets, etc.)


class Asset(models.Model):
    serial_number = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='assets/', null=True, blank=True)
    model = models.CharField(max_length=255)
    model_no = models.CharField(max_length=100)
    category = models.CharField(max_length=255)
    purchase_date = models.DateTimeField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class License(models.Model):
    product_key = models.CharField(max_length=255)
    expiration_date = models.DateTimeField(null=True, blank=True)
    licensed_to_email = models.EmailField()
    licensed_to_name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    total = models.IntegerField()
    purchase_date = models.DateTimeField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class Component(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100)
    category = models.CharField(max_length=255)
    total = models.IntegerField()
    remaining = models.IntegerField()
    min_quantity = models.IntegerField()
    location = models.CharField(max_length=255)
    order_number = models.CharField(max_length=100)
    purchase_date = models.DateTimeField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class Consumable(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='assets/uploads/consumables/', null=True, blank=True)
    category = models.CharField(max_length=255)
    model_no = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    total = models.IntegerField()
    min_quantity = models.IntegerField()
    avail = models.IntegerField()
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class Maintenance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    maintenance_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class Depreciation(models.Model):
    serial_number = models.CharField(max_length=100)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    mapping_status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

# Billitems


class BillItem(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)


# Bills (Vendor Bills, similar to PurchaseInvoice but separate per description)
class Bill(models.Model):
    BILL_TYPE_CHOICES = [
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
    ]
    vendor = models.ForeignKey(
        Party, on_delete=models.CASCADE, limit_choices_to={'type': 'vendor'})
    bill_date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255, null=True, blank=True)  # Optional
    reference = models.CharField(max_length=100)
    memo = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField()
    attachment = models.FileField(
        upload_to='assets/uploads/bills/', null=True, blank=True)
    debit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='debit_bills')
    credit_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='open')
    items = models.ManyToManyField(
        BillItem, related_name='billitems', blank=True)
    bill_type = models.CharField(
        max_length=50, choices=BILL_TYPE_CHOICES, default='withdrawal')
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


# Checks
class Check(models.Model):
    CHECK_TYPE_CHOICES = [
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
    ]
    bank_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, limit_choices_to={'bank_name__isnull': False})
    check_number = models.CharField(max_length=50)
    pay_to = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    memo = models.TextField(null=True, blank=True)
    sign = models.CharField(max_length=255, null=True,
                            blank=True)  # Signature field?
    date = models.DateTimeField(default=timezone.now)
    vendor = models.ForeignKey(Party, on_delete=models.SET_NULL,
                               null=True, blank=True, limit_choices_to={'type': 'vendor'})
    check_type = models.CharField(
        max_length=50, choices=CHECK_TYPE_CHOICES, default='withdrawal')
    status = models.CharField(max_length=50, default='issued')
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

 # Journal Entry (General ledger entries, connecting to accounts)


class JournalEntry(models.Model):
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)


class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(null=True, blank=True)

# Convert


class Convert(models.Model):
    transfer_from = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='transfer_from')
    transfer_to = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='transfer_to')
    transfer_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    transfer_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(
        default=timezone.now, null=True, blank=True)
