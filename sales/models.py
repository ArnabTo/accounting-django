from django.db import models
from accounting.models import Party
# Create your models here.
from django.utils import timezone


class Brands(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class PlotDescription(models.Model):
    plot_no = models.CharField(max_length=100, null=True, blank=True)
    plot_name = models.CharField(max_length=100, null=True, blank=True)
    plot_size = models.CharField(max_length=100, null=True, blank=True)
    plot_type = models.CharField(max_length=100, null=True, blank=True)
    plot_location = models.CharField(max_length=100, null=True, blank=True)
    plot_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    plot_road = models.CharField(max_length=100, null=True, blank=True)
    plot_facing = models.CharField(max_length=100, null=True, blank=True)
    plot_block = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.plot_no


class Item(models.Model):
    ITEM_GROUP = (
        ('raw_material', 'Raw Material'),
        ('manufactured_product', 'Manufactured Product'),
        ('service', 'Service'),
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)

    # Plot description
    plot_description = models.ForeignKey(
        PlotDescription, on_delete=models.CASCADE, null=True, blank=True)

    tax_1 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    tax_2 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    quantity = models.IntegerField(default=1, null=True, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    unit = models.CharField(max_length=50, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    brand = models.ForeignKey(
        Brands, on_delete=models.CASCADE, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    width = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hsn_code = models.CharField(max_length=50, null=True, blank=True)
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    imei = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    item_group = models.CharField(
        choices=ITEM_GROUP, max_length=100, null=True, blank=True)

    status = models.CharField(choices=(
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ), max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Calculate and store subtotal as amount
        if self.plot_description and self.plot_description.plot_price:
            self.name = self.plot_description.plot_name
            self.price = self.quantity * self.plot_description.plot_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Sales(models.Model):
    sales_no = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    related = models.CharField(choices=(
        ('lead', 'Lead'),
        ('customer', 'Customer'),
    ), max_length=100, null=True, blank=True)
    lead_or_customer = models.ForeignKey(
        Party, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    open_till = models.DateField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=100, null=True, blank=True)
    discount_type = models.CharField(choices=(
        ('no_discount', 'No Discount'),
        ('before_tax', 'Before Tax'),
        ('after_tax', 'After Tax'),
    ), max_length=100, null=True, blank=True)
    payment_mode = models.CharField(choices=(
        ('at_a_time', 'At a Tme'),
        ('installment', 'Installment'),
    ), max_length=100, null=True, blank=True)

    tags = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(choices=(
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('open', 'Open'),
        ('revised', 'Revised'),
        ('declined', 'Declined'),
        ('accepted', 'Accepted'),
    ), max_length=100, null=True, blank=True)
    assigned = models.CharField(max_length=100, null=True, blank=True)
    to = models.ForeignKey(Party, on_delete=models.CASCADE,
                           related_name='proposals_to', null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.sales_no


class SalesItems(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="sales_item")
    quantity = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def subtotal(self):
        if self.quantity and self.item:
            return self.quantity * self.item.price
        return 0

    def save(self, *args, **kwargs):
        # Calculate and store subtotal as amount
        if self.quantity and self.item:
            self.amount = self.quantity * self.item.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item.name


class PaymentSchedule(models.Model):
    """Main payment schedule record - stores summary info"""
    sales = models.OneToOneField(
        Sales, on_delete=models.CASCADE, related_name='payment_schedule', null=True, blank=True)

    advance_payment = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    rest_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        sales_no = self.sales.sales_no if self.sales else "No Sales"
        return f"Payment Schedule for {sales_no}"


class PaymentInstallment(models.Model):
    """Individual installment records - only for installment payments"""
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    payment_schedule = models.ForeignKey(
        PaymentSchedule, on_delete=models.CASCADE, related_name='installments')

    payment_time = models.DateField(null=True, blank=True)
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='unpaid')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Installment {self.payment_amount} - {self.payment_time}"

    class Meta:
        ordering = ['payment_time']
