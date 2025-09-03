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
    Depreciation, Bill, BillItem, Check, JournalEntry, JournalEntryLine, ReconcileStatement, ReconcileTransaction, Reconciliation
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


# BankTransaction Serializer
class BankTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    class Meta:
        model = BankTransaction
        fields = '__all__'

# Party Serializer


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = '__all__'

# Item Serializer


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


# InvoiceItem Serializer (for nested items in invoices and bills)
class InvoiceItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    class Meta:
        model = InvoiceItem
        fields = '__all__'


# SalesInvoice Serializer (with nested items for display)
class SalesInvoiceSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, queryset=InvoiceItem.objects.all(), required=False, allow_null=True)

    class Meta:
        model = SalesInvoice
        fields = '__all__'

# SalesPayment Serializer
class SalesPaymentSerializer(serializers.ModelSerializer):
    invoice = serializers.PrimaryKeyRelatedField(queryset=SalesInvoice.objects.all(), required=False, allow_null=True)

    class Meta:
        model = SalesPayment
        fields = '__all__'




# SalesInvoice Serializer (with nested items for display)


class SalesInvoiceSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, queryset=InvoiceItem.objects.all(), required=False, allow_null=True)

    class Meta:
        model = SalesInvoice
        fields = '__all__'

# SalesOrderReturn Serializer


class SalesOrderReturnSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all(), required=False, allow_null=True)
    class Meta:
        model = SalesOrderReturn
        fields = '__all__'

# SalesRefund Serializer


class SalesRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRefund
        fields = '__all__'

# Expense Serializer


class ExpenseGetSerializer(serializers.ModelSerializer):
    vendor = PartySerializer()
    customer = PartySerializer()

    class Meta:
        model = Expense
        fields = '__all__'

class ExpensePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

# Payslip Serializer


class PayslipSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Payslip
        fields = '__all__'

# PurchaseOrder Serializer


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, queryset=PurchaseOrderItem.objects.all(), required=False, allow_null=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

# PurchaseOrderItem Serializer


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    purchase_order = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrder.objects.all(), required=False, allow_null=True)
    item = ItemSerializer()

    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'



# PurchaseInvoice Serializer


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all(), required=False, allow_null=True)
    purchase_order = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrder.objects.all(), required=True, allow_null=True)

    class Meta:
        model = PurchaseInvoice
        fields = '__all__'

# PurchasePayment Serializer


class PurchasePaymentSerializer(serializers.ModelSerializer):
    purchase_order = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrder.objects.all(), required=False, allow_null=True)
    class Meta:
        model = PurchasePayment
        fields = '__all__'

# PurchaseOrderReturn Serializer


class PurchaseOrderReturnSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all(), required=False, allow_null=True)
    class Meta:
        model = PurchaseOrderReturn
        fields = '__all__'

# PurchaseRefund Serializer


class PurchaseRefundSerializer(serializers.ModelSerializer):
    purchase_order_return = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrderReturn.objects.all(), required=False, allow_null=True)
    class Meta:
        model = PurchaseRefund
        fields = '__all__'

# InventoryReceivingVoucher Serializer


class InventoryReceivingVoucherSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, queryset=Item.objects.all(), required=False, allow_null=True)

    class Meta:
        model = InventoryReceivingVoucher
        fields = '__all__'

# StockExport Serializer


class StockExportSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all(), required=False, allow_null=True)
    invoices = serializers.PrimaryKeyRelatedField(many=True, queryset=SalesInvoice.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StockExport
        fields = '__all__'

# LossAdjustment Serializer


class LossAdjustmentSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(many=True, queryset=Item.objects.all(), required=False, allow_null=True)

    class Meta:
        model = LossAdjustment
        fields = '__all__'

# OpeningStock Serializer


class OpeningStockSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), required=False, allow_null=True)

    class Meta:
        model = OpeningStock
        fields = '__all__'

# ManufacturingOrder Serializer


class ManufacturingOrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), required=False, allow_null=True)
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
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Maintenance
        fields = '__all__'

# Depreciation Serializer


class DepreciationSerializer(serializers.ModelSerializer):
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Depreciation
        fields = '__all__'


# Bill Serializer


class BillSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all(), required=False, allow_null=True)
    debit_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    credit_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    items = serializers.PrimaryKeyRelatedField(many=True, queryset=Item.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Bill
        fields = '__all__'

# BillIte# BillItem Serializerm Serializer


class BillItemSerializer(serializers.ModelSerializer):
    bill = serializers.PrimaryKeyRelatedField(queryset=Bill.objects.all(), required=False, allow_null=True)
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), required=False, allow_null=True)

    class Meta:
        model = BillItem
        fields = '__all__'

# Check Serializer


class CheckSerializer(serializers.ModelSerializer):
    bank_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    pay_to = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    vendor = serializers.PrimaryKeyRelatedField(queryset=Party.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Check
        fields = '__all__'

# JournalEntryLine Serializer


class JournalEntryLineSerializer(serializers.ModelSerializer):
    journal_entry = serializers.PrimaryKeyRelatedField(queryset=JournalEntry.objects.all(), required=False, allow_null=True)

    class Meta:
        model = JournalEntryLine
        fields = '__all__'

# JournalEntry Serializer


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True, read_only=True)

    class Meta:
        model = JournalEntry
        fields = '__all__'

class SalesRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRefund
        fields = '__all__'

# Reconciliation Serializers
class ReconcileTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconcileTransaction
        fields = [
            'id', 'statement', 'date', 'transaction_type',
            'account', 'payee', 'description',
            'payment_amount', 'deposit_amount', 'is_cleared'
        ]

class ReconcileStatementSerializer(serializers.ModelSerializer):
    cleared_balance = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    difference = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        read_only=True,
        source='calculate_difference'
    )
    total_payments = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_deposits = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    reconciliation_status = serializers.CharField(
        source='reconciliation.status',
        read_only=True
    )
    
    class Meta:
        model = ReconcileStatement
        fields = [
            'id', 'account', 'beginning_balance',
            'ending_balance', 'ending_date', 'cleared_balance',
            'created_at', 'difference', 'total_payments',
            'total_deposits', 'reconciliation_status'
        ]
        read_only_fields = ['beginning_balance']  # Make beginning_balance read-only

class ReconciliationSerializer(serializers.ModelSerializer):
    statement_difference = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='statement.calculate_difference'
    )
    
    def validate(self, data):
        """
        Check if the reconciliation should be marked as complete
        based on statement difference
        """
        if self.instance:  # If this is an update
            statement = data.get('statement', self.instance.statement)
        else:  # If this is a create
            statement = data.get('statement')
            
        if statement:
            difference = statement.calculate_difference()
            if abs(difference) < 0.01:  # Using small threshold for floating point comparison
                data['status'] = 'completed'
            else:
                data['status'] = 'pending'
        return data

    class Meta:
        model = Reconciliation
        fields = [
            'id', 'statement', 'reconciled_at',
            'status', 'adjustment_amount', 'statement_difference'
        ]
        read_only_fields = ['status']  # Status is automatically set