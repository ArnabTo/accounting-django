from rest_framework import viewsets
from django.shortcuts import render
from . import serializers
from . import models
# Create your views here.


class BrandViewSet(viewsets.ModelViewSet):
    queryset = models.Brands.objects.all()
    serializer_class = serializers.BrandSerializer


class PlotDescriptionViewSet(viewsets.ModelViewSet):
    queryset = models.PlotDescription.objects.all()
    serializer_class = serializers.PlotSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = models.Item.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.ItemReadSerializer
        return serializers.ItemSerializer


class SalesViewSet(viewsets.ModelViewSet):
    queryset = models.Sales.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.SalesReadSerializer
        return serializers.SalesWriteSerializer

    def perform_create(self, serializer):
        if not serializer.validated_data.get('sales_no'):
            serializer.validated_data['sales_no'] = self.generate_sales_number(
            )
        serializer.save()

    def generate_sales_number(self):
        from django.utils.timezone import now
        return f"SALES-{now().strftime('%Y%m%d-%H%M%S')}"


class SalesItemsViewSet(viewsets.ModelViewSet):
    queryset = models.SalesItems.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.SalesItemsReadSerializer
        return serializers.SalesItemsWriteSerializer

    def get_queryset(self):
        queryset = models.SalesItems.objects.all()
        sales_id = self.request.query_params.get('sales_id')
        if sales_id:
            queryset = queryset.filter(sales_id=sales_id)
        return queryset


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    queryset = models.PaymentSchedule.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PaymentScheduleReadSerializer
        return PaymentScheduleWriteSerializer

    def get_queryset(self):
        queryset = PaymentSchedule.objects.all()
        sales_id = self.request.query_params.get('sales_id')
        if sales_id:
            queryset = queryset.filter(sales_id=sales_id)
        return queryset


class PaymentInstallmentViewSet(viewsets.ModelViewSet):
    queryset = models.PaymentInstallment.objects.all()
    serializer_class = serializers.PaymentInstallmentSerializer

    def get_queryset(self):
        queryset = PaymentInstallment.objects.all()
        payment_schedule_id = self.request.query_params.get(
            'payment_schedule_id')
        if payment_schedule_id:
            queryset = queryset.filter(payment_schedule_id=payment_schedule_id)
        return queryset


class SalesPaymentViewSet(viewsets.ModelViewSet):
    queryset = models.SalesPayment.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.SalesPaymentReadSerializer
        return serializers.SalesPaymentSerializer


class SalesInvoiceViewSet(viewsets.ModelViewSet):
    queryset = models.SalesInvoice.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.SalesInvoiceReadSerializer
        return serializers.SalesInvoiceSerializer
