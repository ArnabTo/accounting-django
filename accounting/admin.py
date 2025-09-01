from .models import (AccountName, Account, Party, Item, BankTransaction,
                     SalesPayment, SalesInvoice, SalesOrderReturn,
                     SalesRefund, Expense, Payslip, PurchaseOrder, PurchaseOrderItem,
                     PurchaseInvoice, PurchasePayment, PurchaseOrderReturn,
                     PurchaseRefund, InventoryReceivingVoucher, StockExport,
                     LossAdjustment, OpeningStock, ManufacturingOrder, Asset,
                     License, Component, Consumable, Maintenance, Depreciation,
                     Bill, BillItem, Check, JournalEntry, JournalEntryLine, Order, OrderItem)
from django.contrib import admin
from django.contrib import admin
from .models import AccountName, Account
from django.contrib import admin


@admin.register(AccountName)
class AccountNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_parent_account_name',
                    'balance', 'created_at', 'updated_at')
    list_filter = ('parent_account', 'created_at')
    search_fields = ('parent_account__name', 'name')
    ordering = ('-created_at',)

    def get_parent_account_name(self, obj):
        return obj.parent_account.name if obj.parent_account else 'No Parent'
    get_parent_account_name.short_description = 'Parent Account'


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'email', 'phone', 'status')
    list_filter = ('type', 'status')
    search_fields = ('name', 'email')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'sku', 'price', 'quantity', 'category')
    list_filter = ('type', 'category')
    search_fields = ('name', 'sku')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'seller',
                    'customer', 'total_amount')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'item', 'quantity',
                    'unit_price', 'subtotal')


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'payee',
                    'withdrawal', 'deposit', 'status')
    list_filter = ('status', 'cleared', 'date')
    search_fields = ('payee', 'description')


@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ('date', 'customer', 'amount', 'status')
    list_filter = ('status', 'date')
    search_fields = ('customer__name',)


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'vendor', 'invoice_date',
                    'invoice_amount', 'payment_status')
    list_filter = ('payment_status', 'invoice_date')
    search_fields = ('invoice_no', 'vendor__name')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'category',
                    'purchase_date', 'status')
    list_filter = ('category', 'status')
    search_fields = ('name', 'serial_number')


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('reference', 'vendor', 'bill_date', 'amount', 'status')
    list_filter = ('status', 'bill_date')
    search_fields = ('reference', 'vendor__name')


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('check_number', 'pay_to', 'amount', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('check_number', 'pay_to')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'description')
    list_filter = ('date',)
    search_fields = ('description',)


# Register remaining models with basic ModelAdmin
admin.site.register(SalesPayment)
admin.site.register(SalesOrderReturn)
admin.site.register(SalesRefund)
admin.site.register(Expense)
admin.site.register(Payslip)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(PurchasePayment)
admin.site.register(PurchaseOrderReturn)
admin.site.register(PurchaseRefund)
admin.site.register(InventoryReceivingVoucher)
admin.site.register(StockExport)
admin.site.register(LossAdjustment)
admin.site.register(OpeningStock)
admin.site.register(ManufacturingOrder)
admin.site.register(License)
admin.site.register(Component)
admin.site.register(Consumable)
admin.site.register(Maintenance)
admin.site.register(Depreciation)
admin.site.register(BillItem)
admin.site.register(JournalEntryLine)
