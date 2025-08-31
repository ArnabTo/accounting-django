from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Account, AccountName, BankTransaction, Party,
    Item, SalesPayment, SalesInvoice, SalesOrderReturn, SalesRefund,
    Expense, Payslip, PurchaseOrder, PurchaseInvoice, PurchasePayment,
    PurchaseOrderReturn, PurchaseRefund, InventoryReceivingVoucher, StockExport,
    LossAdjustment,
    OpeningStock, ManufacturingOrder, Asset, License, Component, Consumable,
    Maintenance, Depreciation, Bill, Check, JournalEntry, BillItem
)
from .serializers import (
    AccountSerializer, AccountNameSerializer, BankTransactionSerializer, PartySerializer,
    ItemSerializer, SalesPaymentSerializer, SalesInvoiceSerializer, SalesOrderReturnSerializer, SalesRefundSerializer,
    ExpenseSerializer, PayslipSerializer, PurchaseOrderSerializer, PurchaseInvoiceSerializer, PurchasePaymentSerializer,
    PurchaseOrderReturnSerializer, PurchaseRefundSerializer, InventoryReceivingVoucherSerializer, StockExportSerializer,
    LossAdjustmentSerializer, OpeningStockSerializer, ManufacturingOrderSerializer, AssetSerializer, LicenseSerializer,
    ComponentSerializer, ConsumableSerializer, MaintenanceSerializer, DepreciationSerializer, BillSerializer, CheckSerializer,
    JournalEntrySerializer, BillItemSerializer
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
    serializer_class = SalesInvoiceSerializer


class SalesOrderReturnViewSet(viewsets.ModelViewSet):
    queryset = SalesOrderReturn.objects.all()
    serializer_class = SalesOrderReturnSerializer


class SalesRefundViewSet(viewsets.ModelViewSet):
    queryset = SalesRefund.objects.all()
    serializer_class = SalesRefundSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


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


# class BillViewSet(viewsets.ModelViewSet):
#     queryset = Bill.objects.all()
#     serializer_class = BillSerializer


# class BillItemViewSet(viewsets.ModelViewSet):
#     queryset = BillItem.objects.all()
#     serializer_class = BillItemSerializer


class BillItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BillItem CRUD operations
    All create/update/delete logic is handled in the serializer
    """
    queryset = BillItem.objects.all()
    serializer_class = BillItemSerializer
    filterset_fields = ['quantity', 'cost']
    search_fields = ['description']
    ordering_fields = ['cost', 'quantity', 'amount']
    ordering = ['-id']

    def get_queryset(self):
        """Custom queryset with optimized queries"""
        return BillItem.objects.select_related().prefetch_related('item')

    @action(detail=False, methods=['get'])
    def by_item(self, request):
        """
        Get bill items filtered by specific item ID
        """
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response(
                {'error': 'item_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bill_items = self.get_queryset().filter(item=item_id)
        serializer = self.get_serializer(bill_items, many=True)
        return Response(serializer.data)


class BillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bill CRUD operations
    All create/update/delete logic is handled in the serializer
    """
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    filterset_fields = ['status', 'bill_type',
                        'vendor', 'bill_date', 'due_date']
    search_fields = ['name', 'reference', 'memo', 'vendor__name']
    ordering_fields = ['bill_date', 'due_date', 'amount', 'created_at']
    ordering = ['-bill_date']

    def get_queryset(self):
        """Custom queryset with optimized queries"""
        return Bill.objects.select_related(
            'vendor', 'debit_account', 'credit_account', 'items'
        ).prefetch_related('billitems')

    def get_serializer_class(self):
        """Use different serializer for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            # Check if request includes nested items
            if hasattr(self.request, 'data') and 'bill_items' in self.request.data:
                return BillWithItemsSerializer
        return BillSerializer

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a bill as paid"""
        bill = self.get_object()
        serializer = self.get_serializer(
            bill, data={'status': 'paid'}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_overdue(self, request, pk=None):
        """Mark a bill as overdue"""
        bill = self.get_object()
        serializer = self.get_serializer(
            bill, data={'status': 'overdue'}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def overdue_bills(self, request):
        """Get all overdue bills"""
        from django.utils import timezone
        today = timezone.now().date()

        overdue_bills = self.get_queryset().filter(
            due_date__lt=today,
            status__in=['open', 'pending']
        )

        serializer = self.get_serializer(overdue_bills, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_vendor(self, request):
        """Get bills filtered by vendor"""
        vendor_id = request.query_params.get('vendor_id')
        if not vendor_id:
            return Response(
                {'error': 'vendor_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bills = self.get_queryset().filter(vendor_id=vendor_id)
        serializer = self.get_serializer(bills, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get bill summary statistics"""
        from django.db.models import Sum, Count

        queryset = self.get_queryset()

        summary = {
            'total_bills': queryset.count(),
            'total_amount': queryset.aggregate(Sum('amount'))['amount__sum'] or 0,
            'open_bills': queryset.filter(status='open').count(),
            'paid_bills': queryset.filter(status='paid').count(),
            'overdue_bills': queryset.filter(status='overdue').count(),
            'by_type': {
                'withdrawal': queryset.filter(bill_type='withdrawal').aggregate(
                    count=Count('id'),
                    total=Sum('amount')
                ),
                'deposit': queryset.filter(bill_type='deposit').aggregate(
                    count=Count('id'),
                    total=Sum('amount')
                )
            }
        }

        return Response(summary)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items for a specific bill"""
        bill = self.get_object()
        if bill.items:
            serializer = BillItemSerializer(bill.items)
            return Response(serializer.data)
        return Response({'message': 'No items found for this bill'})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Create a duplicate of the bill"""
        original_bill = self.get_object()

        # Prepare data for duplication
        duplicate_data = {
            'vendor': original_bill.vendor.id,
            'name': f"Copy of {original_bill.name}" if original_bill.name else None,
            'reference': f"{original_bill.reference}-COPY",
            'memo': original_bill.memo,
            'due_date': original_bill.due_date,
            'debit_account': original_bill.debit_account.id if original_bill.debit_account else None,
            'credit_account': original_bill.credit_account.id if original_bill.credit_account else None,
            'amount': original_bill.amount,
            'bill_type': original_bill.bill_type,
            'status': 'open'  # New bills should start as open
        }

        serializer = self.get_serializer(data=duplicate_data)
        if serializer.is_valid():
            new_bill = serializer.save()
            return Response(self.get_serializer(new_bill).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckViewSet(viewsets.ModelViewSet):
    queryset = Check.objects.all()
    serializer_class = CheckSerializer


class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
