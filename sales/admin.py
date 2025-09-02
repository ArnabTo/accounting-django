from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Sales)
admin.site.register(models.SalesItems)
admin.site.register(models.PaymentSchedule)
admin.site.register(models.Brands)
admin.site.register(models.Item)
admin.site.register(models.PaymentInstallment)
admin.site.register(models.SalesPayment)
admin.site.register(models.SalesInvoice)
