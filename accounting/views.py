from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Account, AccountName, BankTransaction, Party,
    Item, SalesPayment, SalesInvoice, SalesOrderReturn, SalesRefund,
    Order,
    Expense, Payslip, PurchaseOrder, PurchaseInvoice, PurchasePayment,
    PurchaseOrderReturn, PurchaseRefund, InventoryReceivingVoucher, StockExport,
    LossAdjustment,
    OpeningStock, ManufacturingOrder, Asset, License, Component, Consumable,
    Maintenance, Depreciation, Bill, Check, JournalEntry, BillItem, Convert
)
from .serializers import (
    AccountSerializer, AccountNameSerializer, BankTransactionSerializer, PartySerializer,
    ItemSerializer,
    SalesPaymentSerializer, SalesInvoiceRead, SalesInvoiceWrite, SalesOrderReturnSerializer, SalesRefundSerializer,
    SalesOrderReturnCreateUpdateSerializer, OrderReadSerializer, OrderWriteSerializer,
    ExpenseReadSerializer, ExpenseWriteSerializer, PayslipSerializer, PurchaseOrderItemReadSerializer, PurchaseOrderItemWriteSerializer,
    PurchaseOrderReadSerializer, PurchaseOrderWriteSerializer,
    PurchaseInvoiceSerializer, PurchasePaymentSerializer,
    PurchaseOrderReturnSerializer, PurchaseRefundSerializer, InventoryReceivingVoucherSerializer, StockExportSerializer,
    LossAdjustmentSerializer, OpeningStockSerializer, ManufacturingOrderSerializer, AssetSerializer, LicenseSerializer,
    ComponentSerializer, ConsumableSerializer, MaintenanceSerializer, DepreciationSerializer, BillSerializer, BillCreateUpdateSerializer, CheckSerializer, CheckCreateUpdateSerializer,
    JournalEntrySerializer, BillItemSerializer, BillItemCreateUpdateSerializer, ConvertCreateSerializer, ConvertSerializer
)


class AccountNameViewSet(viewsets.ModelViewSet):
    queryset = AccountName.objects.all()
    serializer_class = AccountNameSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class BankTransactionViewSet(viewsets.ModelViewSet):
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class SalesPaymentViewSet(viewsets.ModelViewSet):
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer


class SalesInvoiceViewSet(viewsets.ModelViewSet):
    queryset = SalesInvoice.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SalesInvoiceRead
        return SalesInvoiceWrite


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-order_date')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OrderReadSerializer
        return OrderWriteSerializer


class SalesOrderReturnViewSet(viewsets.ModelViewSet):
    queryset = SalesOrderReturn.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SalesOrderReturnSerializer
        return SalesOrderReturnCreateUpdateSerializer


class SalesRefundViewSet(viewsets.ModelViewSet):
    queryset = SalesRefund.objects.all()
    serializer_class = SalesRefundSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ExpenseReadSerializer
        return ExpenseWriteSerializer


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PurchaseOrderReadSerializer
        return PurchaseOrderWriteSerializer


class PurchaseInvoiceViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer


class PurchasePaymentViewSet(viewsets.ModelViewSet):
    queryset = PurchasePayment.objects.all()
    serializer_class = PurchasePaymentSerializer


class PurchaseOrderReturnViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderReturn.objects.all()
    serializer_class = PurchaseOrderReturnSerializer


class PurchaseRefundViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRefund.objects.all()
    serializer_class = PurchaseRefundSerializer


class InventoryReceivingVoucherViewSet(viewsets.ModelViewSet):
    queryset = InventoryReceivingVoucher.objects.all()
    serializer_class = InventoryReceivingVoucherSerializer


class StockExportViewSet(viewsets.ModelViewSet):
    queryset = StockExport.objects.all()
    serializer_class = StockExportSerializer


class LossAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = LossAdjustment.objects.all()
    serializer_class = LossAdjustmentSerializer


class OpeningStockViewSet(viewsets.ModelViewSet):
    queryset = OpeningStock.objects.all()
    serializer_class = OpeningStockSerializer


class ManufacturingOrderViewSet(viewsets.ModelViewSet):
    queryset = ManufacturingOrder.objects.all()
    serializer_class = ManufacturingOrderSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer


class ConsumableViewSet(viewsets.ModelViewSet):
    queryset = Consumable.objects.all()
    serializer_class = ConsumableSerializer


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer


class DepreciationViewSet(viewsets.ModelViewSet):
    queryset = Depreciation.objects.all()
    serializer_class = DepreciationSerializer


class BillItemViewSet(viewsets.ModelViewSet):
    queryset = BillItem.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BillItemSerializer
        return BillItemCreateUpdateSerializer


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BillSerializer   # For GET
        return BillCreateUpdateSerializer  # For POST/PUT/PATCH


class CheckViewSet(viewsets.ModelViewSet):
    queryset = Check.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CheckSerializer   # For GET
        return CheckCreateUpdateSerializer  # For POST/PUT/PATCH


class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer


class ConvertViewSet(viewsets.ModelViewSet):
    queryset = Convert.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ConvertSerializer   # For GET
        return ConvertCreateSerializer  # For POST/PUT/PATCH
