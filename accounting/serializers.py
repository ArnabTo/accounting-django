from django.db import transaction
from rest_framework import serializers
from .models import (
    AccountName, Account,
    BankTransaction, Party,
    Item, SalesPayment,
    SalesInvoice, InvoiceItem,
    SalesOrderReturn, SalesRefund, Expense, Payslip, PurchaseOrder, PurchaseOrderItem,
    PurchaseInvoice, PurchasePayment, PurchaseOrderReturn, PurchaseRefund,
    InventoryReceivingVoucher, StockExport, LossAdjustment, OpeningStock,
    ManufacturingOrder, Asset, License, Component, Consumable, Maintenance,
    Depreciation, Bill, BillItem, Check, JournalEntry, JournalEntryLine
)
from django.utils import timezone


class AccountNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountName
        fields = ['id', 'name', 'balance']


class AccountSerializer(serializers.ModelSerializer):
    parent_account = serializers.PrimaryKeyRelatedField(
        queryset=AccountName.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Account
        fields = [
            'id',
            'account_type',
            'detail_type',
            'name',
            'number',
            'parent_account',
            'balance',
            'as_of',
            'bank_name',
            'bank_account',
            'bank_routing',
            'bank_address',
            'description',
            'status',
        ]

# Party Serializer


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = '__all__'

# BankTransaction Serializer


class BankTransactionSerializer(serializers.ModelSerializer):
    payee = PartySerializer()
    account = AccountSerializer()

    class Meta:
        model = BankTransaction
        fields = '__all__'

# Item Serializer


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

# SalesPayment Serializer


class SalesPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPayment
        fields = '__all__'

# InvoiceItem Serializer (for nested items in invoices and bills)


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'

# SalesInvoice Serializer (with nested items for display)


class SalesInvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer = PartySerializer()
    debit_account = AccountSerializer()
    credit_account = AccountSerializer()

    class Meta:
        model = SalesInvoice
        fields = '__all__'

# SalesOrderReturn Serializer


class SalesOrderReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderReturn
        fields = '__all__'

# SalesRefund Serializer


class SalesRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRefund
        fields = '__all__'

# Expense Serializer


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

# Payslip Serializer


class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = '__all__'

# PurchaseOrderItem Serializer


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'

# PurchaseOrder Serializer


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

# PurchaseInvoice Serializer


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoice
        fields = '__all__'

# PurchasePayment Serializer


class PurchasePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePayment
        fields = '__all__'

# PurchaseOrderReturn Serializer


class PurchaseOrderReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderReturn
        fields = '__all__'

# PurchaseRefund Serializer


class PurchaseRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRefund
        fields = '__all__'

# InventoryReceivingVoucher Serializer


class InventoryReceivingVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryReceivingVoucher
        fields = '__all__'

# StockExport Serializer


class StockExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockExport
        fields = '__all__'

# LossAdjustment Serializer


class LossAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LossAdjustment
        fields = '__all__'

# OpeningStock Serializer


class OpeningStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningStock
        fields = '__all__'

# ManufacturingOrder Serializer


class ManufacturingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturingOrder
        fields = '__all__'

# Asset Serializer


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

# License Serializer


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'

# Component Serializer


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = '__all__'

# Consumable Serializer


class ConsumableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumable
        fields = '__all__'

# Maintenance Serializer


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'

# Depreciation Serializer


class DepreciationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depreciation
        fields = '__all__'

# BillItem Serializer


class BillItemSerializer(serializers.ModelSerializer):
    item_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BillItem
        fields = [
            'id',
            'item',
            'item_details',
            'description',
            'quantity',
            'cost',
            'amount'
        ]

    def get_item_details(self, obj):
        """Return item details for display purposes"""
        if obj.item.exists():
            items = obj.item.all()
            return [
                {
                    'id': item.id,
                    'name': item.name,
                    'sku': item.sku,
                    'type': item.type
                }
                for item in items
            ]
        return []

    def validate(self, data):
        """Custom validation for BillItem"""
        quantity = data.get('quantity', 0)
        cost = data.get('cost', 0)

        if quantity <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than 0")

        if cost < 0:
            raise serializers.ValidationError("Cost cannot be negative")

        return data

    def create(self, validated_data):
        """Custom create logic for BillItem"""
        # Calculate amount if not provided
        if 'amount' not in validated_data:
            validated_data['amount'] = validated_data['quantity'] * \
                validated_data['cost']

        # Extract many-to-many data
        items_data = validated_data.pop('item', [])

        # Create the BillItem instance
        bill_item = BillItem.objects.create(**validated_data)

        # Set many-to-many relationships
        if items_data:
            bill_item.item.set(items_data)

        return bill_item

    def update(self, instance, validated_data):
        """Custom update logic for BillItem"""
        # Extract many-to-many data
        items_data = validated_data.pop('item', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Recalculate amount if quantity or cost changed
        if 'quantity' in validated_data or 'cost' in validated_data:
            instance.amount = instance.quantity * instance.cost

        instance.save()

        # Update many-to-many relationships
        if items_data is not None:
            instance.item.set(items_data)

        return instance


# Bill Serializer


class BillSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    debit_account_name = serializers.CharField(
        source='debit_account.name', read_only=True)
    credit_account_name = serializers.CharField(
        source='credit_account.name', read_only=True)
    items_details = BillItemSerializer(
        source='billitems', many=True, read_only=True)

    class Meta:
        model = Bill
        fields = [
            'id',
            'vendor',
            'vendor_name',
            'bill_date',
            'name',
            'reference',
            'memo',
            'due_date',
            'attachment',
            'debit_account',
            'debit_account_name',
            'credit_account',
            'credit_account_name',
            'amount',
            'status',
            'items',
            'items_details',
            'bill_type',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Custom validation for Bill"""
        bill_date = data.get('bill_date')
        due_date = data.get('due_date')

        if due_date and bill_date and due_date < bill_date:
            raise serializers.ValidationError(
                "Due date cannot be earlier than bill date")

        amount = data.get('amount', 0)
        if amount < 0:
            raise serializers.ValidationError("Amount cannot be negative")

        return data

    def validate_vendor(self, value):
        """Validate that the vendor is actually a vendor type party"""
        if value and value.type != 'vendor':
            raise serializers.ValidationError(
                "Selected party must be a vendor")
        return value

    def validate_reference(self, value):
        """Ensure reference is unique"""
        if self.instance:
            # For updates, exclude current instance
            if Bill.objects.filter(reference=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "Bill with this reference already exists")
        else:
            # For creation
            if Bill.objects.filter(reference=value).exists():
                raise serializers.ValidationError(
                    "Bill with this reference already exists")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Custom create logic for Bill"""
        # Set created_at and updated_at
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()

        # Create the bill instance
        bill = Bill.objects.create(**validated_data)

        # If bill_type is withdrawal, ensure we have proper accounts set
        if bill.bill_type == 'withdrawal' and not bill.credit_account:
            # You might want to set a default account or raise validation error
            pass

        return bill

    @transaction.atomic
    def update(self, instance, validated_data):
        """Custom update logic for Bill"""
        # Update the updated_at field
        validated_data['updated_at'] = timezone.now()

        # Store old status for comparison
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Custom logic when status changes
        if old_status != new_status:
            self._handle_status_change(instance, old_status, new_status)

        instance.save()
        return instance

    def _handle_status_change(self, instance, old_status, new_status):
        """Handle business logic when bill status changes"""
        if new_status == 'paid':
            # Logic when bill is marked as paid
            # e.g., create journal entries, update inventory, etc.
            pass
        elif new_status == 'cancelled':
            # Logic when bill is cancelled
            pass
        elif new_status == 'overdue':
            # Logic for overdue bills
            # e.g., send notifications, apply penalties, etc.
            pass

    def to_representation(self, instance):
        """Customize the output representation"""
        data = super().to_representation(instance)

        # Add computed fields
        data['days_until_due'] = None
        if instance.due_date:
            from datetime import date
            today = date.today()
            days_diff = (instance.due_date - today).days
            data['days_until_due'] = days_diff
            data['is_overdue'] = days_diff < 0

        # Add total items count
        if hasattr(instance, 'billitems'):
            data['total_items'] = instance.billitems.count(
            ) if instance.billitems else 0

        return data

# Check Serializer


class CheckSerializer(serializers.ModelSerializer):
    pay_to = AccountSerializer(read_only=True)
    bank_account = AccountSerializer(read_only=True)
    vendor = PartySerializer(read_only=True)

    class Meta:
        model = Check
        fields = '__all__'

# JournalEntryLine Serializer


class JournalEntryLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntryLine
        fields = '__all__'

# JournalEntry Serializer


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True, read_only=True)

    class Meta:
        model = JournalEntry
        fields = '__all__'
