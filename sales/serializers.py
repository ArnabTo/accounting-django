from . import models
from rest_framework import serializers
from accounting.serializers import PartySerializer


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brands
        fields = ['id', 'name', 'description']


class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlotDescription
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = '__all__'


class ItemReadSerializer(serializers.ModelSerializer):
    plot_description = PlotSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = models.Item
        fields = '__all__'

# Sales Serializers


class SalesItemsReadSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = models.SalesItems
        fields = ['id', 'item', 'quantity',
                  'amount', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['subtotal'] = instance.subtotal()
        return data


class PaymentScheduleReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentSchedule
        fields = ['id', 'advance_payment', 'rest_amount', ]


class SalesReadSerializer(serializers.ModelSerializer):
    lead_or_customer = PartySerializer(read_only=True)
    to = PartySerializer(read_only=True)
    items = SalesItemsReadSerializer(
        source='salesitems_set', many=True, read_only=True)
    payment_schedule = PaymentScheduleReadSerializer(read_only=True)

    class Meta:
        model = models.Sales
        fields = ['id', 'sales_no', 'subject', 'related', 'lead_or_customer',
                  'date', 'open_till', 'amount', 'currency', 'discount_type',
                  'payment_mode', 'tags', 'status', 'assigned', 'to', 'created_at',
                  'updated_at', 'items', 'payment_schedule']


class SalesItemsWriteSerializer(serializers.ModelSerializer):
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Item.objects.all(), source='item')

    class Meta:
        model = models.SalesItems
        fields = ['item_id', 'quantity']

    def to_internal_value(self, data):
        if isinstance(data.get('item_id'), dict):
            data = data.copy()
            data['item_id'] = data['item_id'].get('id')
        return super().to_internal_value(data)


class PaymentInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentInstallment
        fields = ['id', 'payment_time', 'payment_amount',
                  'status', 'created_at', 'updated_at']


class PaymentScheduleReadSerializer(serializers.ModelSerializer):
    installments = PaymentInstallmentSerializer(many=True, read_only=True)

    class Meta:
        model = models.PaymentSchedule
        fields = ['id', 'advance_payment', 'rest_amount',
                  'created_at', 'updated_at', 'installments']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Get the sales payment_mode to determine structure
        sales = instance.sales

        if sales.payment_mode == 'at_a_time':
            # For at_a_time, only return advance_payment and rest_amount
            return {
                'advance_payment': data['advance_payment'],
                'rest_amount': data['rest_amount']
            }
        else:
            # For installment, return full structure
            return {
                'advance_payment': data['advance_payment'],
                'rest_amount': data['rest_amount'],
                'installments': data['installments']
            }


class PaymentScheduleWriteSerializer(serializers.ModelSerializer):
    installments = PaymentInstallmentSerializer(
        many=True, write_only=True, required=False)

    class Meta:
        model = models.PaymentSchedule
        fields = ['advance_payment', 'rest_amount', 'installments', 'sales']

    def create(self, validated_data):
        print(validated_data)
        installments_data = validated_data.pop('installments', [])
        # Ensure sales is provided in validated_data
        if 'sales' not in validated_data:
            raise serializers.ValidationError(
                "Sales field is required for PaymentSchedule.")

        # Create PaymentSchedule instance
        payment_schedule = models.PaymentSchedule.objects.create(
            **validated_data)

        # Access sales after ensuring it's saved
        sales = payment_schedule.sales
        if sales and sales.payment_mode == 'installment':
            for installment_data in installments_data:
                models.PaymentInstallment.objects.create(
                    payment_schedule=payment_schedule,
                    **installment_data
                )

        return payment_schedule


class SalesWriteSerializer(serializers.ModelSerializer):
    items = SalesItemsWriteSerializer(many=True, write_only=True)
    payment_schedule = PaymentScheduleWriteSerializer(
        write_only=True, required=False)

    class Meta:
        model = models.Sales
        fields = ['sales_no', 'subject', 'related', 'lead_or_customer',
                  'date', 'open_till', 'amount', 'currency', 'discount_type',
                  'payment_mode', 'tags', 'status', 'assigned', 'to',
                  'items', 'payment_schedule']
        extra_kwargs = {
            'sales_no': {'required': False},
            'amount': {'required': False},
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        payment_schedule_data = validated_data.pop('payment_schedule', None)

        sales = models.Sales.objects.create(**validated_data)

        # Create sales items
        total_amount = 0
        for item_data in items_data:
            sales_item = models.SalesItems.objects.create(
                sales=sales, **item_data)
            total_amount += sales_item.subtotal()

        # Update sales amount if not provided
        if not sales.amount:
            sales.amount = total_amount
            sales.save(update_fields=['amount'])

        # Create payment schedule (for both at_a_time and installment)
        if payment_schedule_data:
            payment_schedule_data['sales'] = sales.id
            print(payment_schedule_data, '============================>>')
            payment_schedule_serializer = PaymentScheduleWriteSerializer(
                data=payment_schedule_data)
            print(payment_schedule_serializer.is_valid())
            if payment_schedule_serializer.is_valid():
                payment_schedule_serializer.save()

        return sales

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        payment_schedule_data = validated_data.pop('payment_schedule', None)

        # Update Sales fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update items
        if items_data is not None:
            instance.salesitems_set.all().delete()

            total_amount = 0
            for item_data in items_data:
                sales_item = models.SalesItems.objects.create(
                    sales=instance, **item_data)
                total_amount += sales_item.subtotal()

            instance.amount = total_amount
            instance.save(update_fields=['amount'])

        # Update payment schedule
        if payment_schedule_data is not None:
            # Delete existing payment schedule and installments
            try:
                instance.payment_schedule.delete()
            except PaymentSchedule.DoesNotExist:
                pass

            # Create new payment schedule
            payment_schedule_data['sales'] = instance
            payment_schedule_serializer = PaymentScheduleWriteSerializer(
                data=payment_schedule_data)
            if payment_schedule_serializer.is_valid():
                payment_schedule_serializer.save()

        return instance
