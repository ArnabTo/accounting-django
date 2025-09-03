from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sales', views.SalesViewSet)
router.register(r'sales-items', views.SalesItemsViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'plot-descriptions', views.PlotDescriptionViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'sales-payments', views.SalesPaymentViewSet)
router.register(r'sales-invoices', views.SalesInvoiceViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
