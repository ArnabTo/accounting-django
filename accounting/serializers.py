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
    bill = serializers.PrimaryKeyRelatedField(read_only=True)
    # accept item ID for posting
    item = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = BillItem
        fields = '__all__'

# Bill Serializer


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, write_only=True)   # for input
    bill_items = BillItemSerializer(
        source='billitem_set', many=True, read_only=True)    # for output
    debit_account = AccountSerializer(read_only=True)
    credit_account = AccountSerializer(read_only=True)
    vendor = PartySerializer(read_only=True)

    class Meta:
        model = Bill
        fields = (
            'id', 'vendor', 'bill_date', 'name', 'reference', 'memo',
            'due_date', 'attachment', 'debit_account', 'credit_account',
            'amount', 'status', 'bill_type', 'created_at', 'updated_at',
            'items', 'bill_items'
        )

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = Bill.objects.create(**validated_data)

        for item_data in items_data:
            BillItem.objects.create(bill=bill, **item_data)

        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        # update bill fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # replace bill items
        if items_data:
            instance.billitem_set.all().delete()
            for item_data in items_data:
                BillItem.objects.create(bill=instance, **item_data)

        return instance

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
