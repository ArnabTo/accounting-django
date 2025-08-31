import logging
from .models import Account, SalesInvoice
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from .models import (
    Account, BankTransaction, SalesInvoice, SalesPayment, SalesRefund, Expense,
    PurchaseInvoice, PurchasePayment, PurchaseRefund, Bill, Check, JournalEntryLine,
    InventoryReceivingVoucher, StockExport, LossAdjustment, Depreciation, ManufacturingOrder
)

# Helper function to update account balance
# Assumption: Account.balance is a simplified net balance.
# - For debit-normal accounts (e.g., assets, expenses), debit increases balance, credit decreases.
# - For credit-normal accounts (e.g., liabilities, revenue), credit increases balance, debit decreases.
# For simplicity, we assume Account.balance is affected as:
# - debit_account.balance += amount for debit entries
# - credit_account.balance += amount for credit entries (assuming positive balance for credit-normal accounts)
# If account_type matters, we can add logic to check 'debit'/'credit' type, but for now, keep it straightforward.
# This is a simplification; real accounting ensures debits = credits, but we update per account.


def update_account_balance(account, amount_delta):
    if account:
        account.balance = (account.balance or 0) + amount_delta
        account.save(update_fields=['balance'])

# BankTransaction signal


@receiver(pre_save, sender=BankTransaction)
def capture_old_bank_transaction(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_deposit = old.deposit
        instance._old_withdrawal = old.withdrawal
    else:
        instance._old_deposit = 0
        instance._old_withdrawal = 0


@receiver(post_save, sender=BankTransaction)
def update_bank_transaction_balance(sender, instance, created, **kwargs):
    old_delta = instance._old_deposit - instance._old_withdrawal
    new_delta = instance.deposit - instance.withdrawal
    net_delta = new_delta - old_delta if not created else new_delta
    update_account_balance(instance.account, net_delta)


@receiver(pre_delete, sender=BankTransaction)
def reverse_bank_transaction_balance(sender, instance, **kwargs):
    delta = instance.withdrawal - instance.deposit  # Reverse effect
    update_account_balance(instance.account, delta)

# SalesInvoice signal


# Helper function to update account balance, respecting account_type
def update_account_balance(account, amount_delta, is_debit=True):
    if account:
        # If debit to debit-normal (asset/expense) or credit to credit-normal (liability/revenue), increase balance
        if (is_debit and account.account_type == 'debit') or (not is_debit and account.account_type == 'credit'):
            account.balance = (account.balance or 0) + amount_delta
        else:
            # If debit to credit-normal or credit to debit-normal, decrease balance
            account.balance = (account.balance or 0) - amount_delta
        account.save(update_fields=['balance'])

# SalesInvoice signals


# Set up logging
logger = logging.getLogger(__name__)


def update_account_balance(account, amount_delta, is_debit=True):
    if not account:
        logger.error("No account provided for balance update")
        return
    current_balance = account.balance or 0
    if is_debit:
        # Debit: increase debit-normal (asset/expense), decrease credit-normal (liability/revenue)
        if account.account_type == 'debit':
            new_balance = current_balance + amount_delta
            logger.debug(
                f"Debiting {account.name} (debit-normal): {current_balance} + {amount_delta} = {new_balance}")
        else:
            new_balance = current_balance - amount_delta
            logger.debug(
                f"Debiting {account.name} (credit-normal): {current_balance} - {amount_delta} = {new_balance}")
    else:
        # Credit: increase credit-normal, decrease debit-normal
        if account.account_type == 'credit':
            new_balance = current_balance + amount_delta
            logger.debug(
                f"Crediting {account.name} (credit-normal): {current_balance} + {amount_delta} = {new_balance}")
        else:
            new_balance = current_balance - amount_delta
            logger.debug(
                f"Crediting {account.name} (debit-normal): {current_balance} - {amount_delta} = {new_balance}")
    account.balance = new_balance
    account.save(update_fields=['balance'])


@receiver(pre_save, sender=SalesInvoice)
def capture_old_sales_invoice(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_amount = old.amount
        except sender.DoesNotExist:
            instance._old_amount = 0
    else:
        instance._old_amount = 0
    logger.debug(
        f"Captured old amount for SalesInvoice {instance.pk}: {instance._old_amount}")


@receiver(post_save, sender=SalesInvoice)
def update_sales_invoice_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    logger.debug(
        f"SalesInvoice {instance.id}: net_delta={net_delta}, created={created}")
    if instance.debit_account:
        update_account_balance(instance.debit_account,
                               net_delta, is_debit=True)
    if instance.credit_account:
        update_account_balance(instance.credit_account,
                               net_delta, is_debit=False)


@receiver(pre_delete, sender=SalesInvoice)
def reverse_sales_invoice_balance(sender, instance, **kwargs):
    logger.debug(
        f"Reversing SalesInvoice {instance.id}: amount={instance.amount}")
    if instance.debit_account:
        update_account_balance(instance.debit_account,
                               instance.amount, is_debit=False)  # Reverse debit
    if instance.credit_account:
        update_account_balance(instance.credit_account,
                               instance.amount, is_debit=True)  # Reverse credit

# SalesPayment signal


@receiver(pre_save, sender=SalesPayment)
def capture_old_sales_payment(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=SalesPayment)
def update_sales_payment_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    if instance.invoice and instance.invoice.debit_account:
        update_account_balance(
            instance.invoice.debit_account, -net_delta)  # Reduce receivable
    # Note: Ideally, credit a bank/cash account, but model lacks it. Add Account FK if needed.


@receiver(pre_delete, sender=SalesPayment)
def reverse_sales_payment_balance(sender, instance, **kwargs):
    if instance.invoice and instance.invoice.debit_account:
        update_account_balance(instance.invoice.debit_account, instance.amount)

# SalesRefund signal


@receiver(pre_save, sender=SalesRefund)
def capture_old_sales_refund(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=SalesRefund)
def update_sales_refund_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    # Assume refund decreases bank (needs bank_account FK) and increases receivable or expense
    # For now, skip since no account link; add FK to Account if needed.
    pass


@receiver(pre_delete, sender=SalesRefund)
def reverse_sales_refund_balance(sender, instance, **kwargs):
    pass  # Reverse if FK added

# Expense signal


@receiver(pre_save, sender=Expense)
def capture_old_expense(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=Expense)
def update_expense_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    if instance.account:
        # Debit expense account
        update_account_balance(instance.account, net_delta)


@receiver(pre_delete, sender=Expense)
def reverse_expense_balance(sender, instance, **kwargs):
    if instance.account:
        update_account_balance(instance.account, -instance.amount)

# PurchaseInvoice signal
# Note: PurchaseInvoice lacks debit/credit_account; consider adding like SalesInvoice


@receiver(pre_save, sender=PurchaseInvoice)
def capture_old_purchase_invoice(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.invoice_amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=PurchaseInvoice)
def update_purchase_invoice_balance(sender, instance, created, **kwargs):
    net_delta = instance.invoice_amount - \
        instance._old_amount if not created else instance.invoice_amount
    # Add debit_account, credit_account to model for proper accounting
    # e.g., debit expense/asset, credit payable
    pass  # Implement if accounts added


@receiver(pre_delete, sender=PurchaseInvoice)
def reverse_purchase_invoice_balance(sender, instance, **kwargs):
    pass  # Implement if accounts added

# PurchasePayment signal


@receiver(pre_save, sender=PurchasePayment)
def capture_old_purchase_payment(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=PurchasePayment)
def update_purchase_payment_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    # Assume decreases payable, decreases bank (needs bank_account FK)
    pass  # Implement if accounts added


@receiver(pre_delete, sender=PurchasePayment)
def reverse_purchase_payment_balance(sender, instance, **kwargs):
    pass  # Implement if accounts added

# PurchaseRefund signal


@receiver(pre_save, sender=PurchaseRefund)
def capture_old_purchase_refund(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=PurchaseRefund)
def update_purchase_refund_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    # Assume increases bank, increases payable/expense (needs account FK)
    pass  # Implement if accounts added


@receiver(pre_delete, sender=PurchaseRefund)
def reverse_purchase_refund_balance(sender, instance, **kwargs):
    pass  # Implement if accounts added

# Bill signal


@receiver(pre_save, sender=Bill)
def capture_old_bill(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=Bill)
def update_bill_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount

    # Update account balances
    if instance.debit_account:
        update_account_balance(instance.debit_account,
                               net_delta)  # Debit expense/asset
    if instance.credit_account:
        update_account_balance(instance.credit_account,
                               net_delta)  # Credit payable

    # Create corresponding bank transaction for new bills
    if created:
        withdrawal_amount = instance.amount if instance.bill_type == 'withdrawal' else 0
        deposit_amount = instance.amount if instance.bill_type == 'deposit' else 0

        BankTransaction.objects.create(
            account=instance.credit_account,
            date=instance.bill_date,
            payee=instance.vendor,
            description=instance.memo or f"Bill {instance.reference}",
            withdrawal=withdrawal_amount,
            deposit=deposit_amount,
            status='pending'
        )


@receiver(pre_delete, sender=Bill)
def reverse_bill_balance(sender, instance, **kwargs):
    if instance.debit_account:
        update_account_balance(instance.debit_account, -instance.amount)
    if instance.credit_account:
        update_account_balance(instance.credit_account, -instance.amount)

# Check signal


@receiver(pre_save, sender=Check)
def capture_old_check(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=Check)
def update_check_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    if instance.bank_account:
        update_account_balance(instance.bank_account, -
                               net_delta)  # Decrease bank

    if instance.pay_to:
        update_account_balance(instance.pay_to, net_delta)  # Increase pay_to

    # Create corresponding bank transaction for new checks
    if created:
        withdrawal_amount = instance.amount if instance.check_type == 'withdrawal' else 0
        deposit_amount = instance.amount if instance.check_type == 'deposit' else 0

        BankTransaction.objects.create(
            account=instance.bank_account,
            date=instance.date,
            payee=instance.vendor,
            description=instance.memo or f"Check #{instance.check_number}",
            withdrawal=withdrawal_amount,
            deposit=deposit_amount,
            status='pending'
        )


@receiver(pre_delete, sender=Check)
def reverse_check_balance(sender, instance, **kwargs):
    if instance.bank_account:
        update_account_balance(instance.bank_account, instance.amount)

# JournalEntryLine signal


@receiver(pre_save, sender=JournalEntryLine)
def capture_old_journal_line(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_debit = old.debit
        instance._old_credit = old.credit
    else:
        instance._old_debit = 0
        instance._old_credit = 0


@receiver(post_save, sender=JournalEntryLine)
def update_journal_line_balance(sender, instance, created, **kwargs):
    old_delta = instance._old_debit - instance._old_credit
    new_delta = instance.debit - instance.credit
    net_delta = new_delta - old_delta if not created else new_delta
    update_account_balance(instance.account, net_delta)


@receiver(pre_delete, sender=JournalEntryLine)
def reverse_journal_line_balance(sender, instance, **kwargs):
    delta = instance.credit - instance.debit  # Reverse
    update_account_balance(instance.account, delta)

# InventoryReceivingVoucher signal


@receiver(pre_save, sender=InventoryReceivingVoucher)
def capture_old_inventory_receiving(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_value = old.value_of_inventory
    else:
        instance._old_value = 0


@receiver(post_save, sender=InventoryReceivingVoucher)
def update_inventory_receiving_balance(sender, instance, created, **kwargs):
    net_delta = instance.value_of_inventory - \
        instance._old_value if not created else instance.value_of_inventory
    # Debit inventory asset account, credit payable if unpaid
    # Needs Account FK; for now, skip or add field
    pass


@receiver(pre_delete, sender=InventoryReceivingVoucher)
def reverse_inventory_receiving_balance(sender, instance, **kwargs):
    pass  # Implement with account FK

# StockExport signal


@receiver(pre_save, sender=StockExport)
def capture_old_stock_export(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = 0  # Estimate via invoices if needed
    else:
        instance._old_amount = 0


@receiver(post_save, sender=StockExport)
def update_stock_export_balance(sender, instance, created, **kwargs):
    # Decrease inventory, increase COGS (cost of goods sold)
    # Needs account links and amount calculation
    pass


@receiver(pre_delete, sender=StockExport)
def reverse_stock_export_balance(sender, instance, **kwargs):
    pass

# LossAdjustment signal


@receiver(pre_save, sender=LossAdjustment)
def capture_old_loss_adjustment(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = 0  # Estimate via items if needed
    else:
        instance._old_amount = 0


@receiver(post_save, sender=LossAdjustment)
def update_loss_adjustment_balance(sender, instance, created, **kwargs):
    # Debit loss/expense, credit inventory
    pass


@receiver(pre_delete, sender=LossAdjustment)
def reverse_loss_adjustment_balance(sender, instance, **kwargs):
    pass

# Depreciation signal


@receiver(pre_save, sender=Depreciation)
def capture_old_depreciation(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_amount = old.amount
    else:
        instance._old_amount = 0


@receiver(post_save, sender=Depreciation)
def update_depreciation_balance(sender, instance, created, **kwargs):
    net_delta = instance.amount - instance._old_amount if not created else instance.amount
    # Debit depreciation expense, credit accumulated depreciation
    # Needs account links (Asset could link to Account)
    pass


@receiver(pre_delete, sender=Depreciation)
def reverse_depreciation_balance(sender, instance, **kwargs):
    pass

# ManufacturingOrder signal


@receiver(pre_save, sender=ManufacturingOrder)
def capture_old_manufacturing_order(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        instance._old_quantity = old.quantity
        instance._old_cost = old.product.cost or 0
    else:
        instance._old_quantity = 0
        instance._old_cost = 0


@receiver(post_save, sender=ManufacturingOrder)
def update_manufacturing_order_balance(sender, instance, created, **kwargs):
    old_amount = instance._old_quantity * instance._old_cost
    new_amount = instance.quantity * (instance.product.cost or 0)
    net_delta = new_amount - old_amount if not created else new_amount
    # Debit finished goods, credit raw materials/WIP
    pass


@receiver(pre_delete, sender=ManufacturingOrder)
def reverse_manufacturing_order_balance(sender, instance, **kwargs):
    pass
