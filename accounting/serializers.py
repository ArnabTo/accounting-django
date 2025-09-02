from django.db import transaction
from rest_framework import serializers
from .models import (
    AccountName, Account,
    BankTransaction, Party,
    Item, SalesPayment,
    SalesInvoice,
    SalesOrderReturn, SalesRefund, Expense, Payslip, PurchaseOrder, PurchaseOrderItem,
    PurchaseInvoice, PurchasePayment, PurchaseOrderReturn, PurchaseRefund,
    InventoryReceivingVoucher, StockExport, LossAdjustment, OpeningStock,
    ManufacturingOrder, Asset, License, Component, Consumable, Maintenance,
    Depreciation, Bill, BillItem, Check, JournalEntry, JournalEntryLine, Convert, Order, OrderItem
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


class OrderItemReadSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'quantity', 'unit_price', 'subtotal']


class OrderReadSerializer(serializers.ModelSerializer):
    customer = PartySerializer(read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'seller', 'order_date',
                  'payment_mode', 'customer', 'total_amount', 'items']


class OrderItemWriteSerializer(serializers.ModelSerializer):
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(), source='item')

    class Meta:
        model = OrderItem
        fields = ['item_id', 'quantity', 'unit_price']


class OrderWriteSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        # Optional: calculate total
        order.calculate_total()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.seller = validated_data.get('seller', instance.seller)
        instance.payment_mode = validated_data.get(
            'payment_mode', instance.payment_mode)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.save()

        if items_data is not None:
            # Remove existing items and add new
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        instance.calculate_total()
        return instance

# SalesInvoice Serializer (with nested items for display)


class SalesInvoiceRead(serializers.ModelSerializer):
    order = OrderReadSerializer(read_only=True)

    class Meta:
        model = SalesInvoice
        fields = '__all__'


class SalesInvoiceWrite(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoice
        fields = '__all__'


# SalesOrderReturn Serializer


class SalesOrderReturnCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderReturn
        fields = '__all__'


class SalesOrderReturnSerializer(serializers.ModelSerializer):
    order = OrderReadSerializer(read_only=True)

    class Meta:
        model = SalesOrderReturn
        fields = '__all__'
# SalesRefund Serializer


class SalesRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRefund
        fields = '__all__'

# Expense Serializer


class ExpenseReadSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'


class ExpenseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

# Payslip Serializer


class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = '__all__'


# PurchaseOrder Serializers

class PurchaseOrderItemReadSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'item', 'quantity', 'unit_price', 'subtotal']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['subtotal'] = instance.subtotal()
        return data


class PurchaseOrderReadSerializer(serializers.ModelSerializer):
    vendor = PartySerializer(read_only=True)
    items = PurchaseOrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'purchase_order', 'po_value', 'tax_value',
                  'total_including_tax', 'vendor', 'order_date',
                  'payment_status', 'payment_request_status', 'payment_mode',
                  'expense_of', 'mapping_status', 'created_at',
                  'updated_at', 'items']


class PurchaseOrderItemWriteSerializer(serializers.ModelSerializer):
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(), source='item')

    class Meta:
        model = PurchaseOrderItem
        fields = ['item_id', 'quantity', 'unit_price']

    def to_internal_value(self, data):
        # Handle case where item_id is sent as a dict with 'id' key
        if isinstance(data.get('item_id'), dict):
            data = data.copy()
            data['item_id'] = data['item_id'].get('id')
        return super().to_internal_value(data)


class PurchaseOrderWriteSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False},
            'updated_at': {'required': False},
            'mapping_status': {'required': False},
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)

        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order, **item_data)

        # Calculate total
        purchase_order.calculate_total()
        return purchase_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update PurchaseOrder fields
        instance.purchase_order = validated_data.get(
            'purchase_order', instance.purchase_order)
        instance.po_value = validated_data.get('po_value', instance.po_value)
        instance.tax_value = validated_data.get(
            'tax_value', instance.tax_value)
        instance.total_including_tax = validated_data.get(
            'total_including_tax', instance.total_including_tax)
        instance.vendor = validated_data.get('vendor', instance.vendor)
        instance.order_date = validated_data.get(
            'order_date', instance.order_date)
        instance.payment_status = validated_data.get(
            'payment_status', instance.payment_status)
        instance.expense_of = validated_data.get(
            'expense_of', instance.expense_of)
        instance.mapping_status = validated_data.get(
            'mapping_status', instance.mapping_status)
        instance.updated_at = timezone.now()
        instance.save()

        if items_data is not None:
            # Remove existing items and add new ones
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseOrderItem.objects.create(
                    purchase_order=instance, **item_data)

            instance.calculate_total()

        return instance


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
    item_details = ItemSerializer(read_only=True)

    class Meta:
        model = BillItem
        fields = '__all__'


class BillItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = '__all__'

# Bill Serializer


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)
    vendor = PartySerializer(read_only=True)
    debit_account = AccountSerializer(read_only=True)
    credit_account = AccountSerializer(read_only=True)

    class Meta:
        model = Bill
        fields = '__all__'


class BillCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'


# Check Serializer


class CheckCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Check
        fields = '__all__'


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


class ConvertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convert
        fields = '__all__'


class ConvertSerializer(serializers.ModelSerializer):
    transfer_from = AccountSerializer(read_only=True)
    transfer_to = AccountSerializer(read_only=True)

    class Meta:
        model = Convert
        fields = '__all__'
