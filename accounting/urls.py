from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountNameViewSet, AccountViewSet,
    BankTransactionViewSet, PartyViewSet,
    ItemViewSet, SalesPaymentViewSet, OrderViewSet,
    SalesInvoiceViewSet, SalesOrderReturnViewSet,
    SalesRefundViewSet, ExpenseViewSet,
    PayslipViewSet, PurchaseOrderViewSet,
    PurchaseInvoiceViewSet, PurchasePaymentViewSet,
    PurchaseOrderReturnViewSet, PurchaseRefundViewSet,
    InventoryReceivingVoucherViewSet, StockExportViewSet,
    LossAdjustmentViewSet, OpeningStockViewSet,
    ManufacturingOrderViewSet, AssetViewSet, LicenseViewSet,
    ComponentViewSet, ConsumableViewSet, MaintenanceViewSet,
    DepreciationViewSet, BillViewSet, BillItemViewSet, CheckViewSet,
    JournalEntryViewSet, ConvertViewSet
)

router = DefaultRouter()
router.register(r'account-names', AccountNameViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'bank-transactions', BankTransactionViewSet)
router.register(r'parties', PartyViewSet)
# router.register(r'items', ItemViewSet)
# router.register(r'sales-payments', SalesPaymentViewSet)
# router.register(r'sales-invoices', SalesInvoiceViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'sales-order-returns', SalesOrderReturnViewSet)
router.register(r'sales-refunds', SalesRefundViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'payslips', PayslipViewSet)
router.register(r'purchase-orders', PurchaseOrderViewSet)
router.register(r'purchase-invoices', PurchaseInvoiceViewSet)
router.register(r'purchase-payments', PurchasePaymentViewSet)
router.register(r'purchase-order-returns', PurchaseOrderReturnViewSet)
router.register(r'purchase-refunds', PurchaseRefundViewSet)
router.register(r'inventory-receiving-vouchers',
                InventoryReceivingVoucherViewSet)
router.register(r'stock-exports', StockExportViewSet)
router.register(r'loss-adjustments', LossAdjustmentViewSet)
router.register(r'opening-stocks', OpeningStockViewSet)
router.register(r'manufacturing-orders', ManufacturingOrderViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'licenses', LicenseViewSet)
router.register(r'components', ComponentViewSet)
router.register(r'consumables', ConsumableViewSet)
router.register(r'maintenances', MaintenanceViewSet)
router.register(r'depreciations', DepreciationViewSet)
router.register(r'bills', BillViewSet)
router.register(r'bill-items', BillItemViewSet)
router.register(r'checks', CheckViewSet)
router.register(r'journal-entries', JournalEntryViewSet)
router.register(r'converts', ConvertViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
