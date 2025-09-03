from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from .models import Sales, SalesInvoice, SalesPayment, Account


@receiver(post_save, sender=Sales)
def create_sales_invoice_and_payment(sender, instance, created, **kwargs):
    """
    Create SalesInvoice and SalesPayment when Sales is created or updated with amount
    """
    # Check if invoice already exists to avoid duplicates
    if (instance.amount and instance.amount > 0 and
            not SalesInvoice.objects.filter(sales=instance).exists()):
        with transaction.atomic():
            # Get or create default accounts
            debit_account = Account.objects.filter(
                account_type='debit').first()
            credit_account = Account.objects.filter(
                account_type='credit').first()

            # Create SalesInvoice
            invoice = SalesInvoice.objects.create(
                sales=instance,
                date=instance.date or timezone.now(),
                amount=instance.amount,
                customer=instance.lead_or_customer,
                status='open',
                debit_account=debit_account,
                credit_account=credit_account,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            # Get plot information from the first sales item if available
            plot_info = {}
            if hasattr(instance, 'salesitems_set'):
                first_sales_item = instance.salesitems_set.first()
                if first_sales_item and first_sales_item.item and first_sales_item.item.plot_description:
                    plot_desc = first_sales_item.item.plot_description
                    plot_info = {
                        'plot_no': plot_desc.plot_no,
                        'road_no': plot_desc.plot_road,
                        'block': plot_desc.plot_block,
                        'area': plot_desc.plot_location,
                    }

            # Create SalesPayment
            SalesPayment.objects.create(
                date=instance.date or timezone.now(),
                amount=instance.amount,
                payment_mode=instance.payment_mode or 'cash',
                name_of_purchaser=instance.lead_or_customer.name if instance.lead_or_customer else '',
                against=f"Sales Order: {instance.sales_no}",
                plot_no=plot_info.get('plot_no', ''),
                road_no=plot_info.get('road_no', ''),
                block=plot_info.get('block', ''),
                area=plot_info.get('area', ''),
                project=instance.subject or '',
                invoice=invoice,
                status='paid' if instance.status == 'accepted' else 'pending',
                mapping_status='auto_created',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
