from django.contrib import admin
from django.contrib import admin
from .models import AccountName, Account

@admin.register(AccountName)
class AccountNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_parent_account_name', 'balance', 'created_at', 'updated_at')
    list_filter = ('parent_account', 'created_at')
    search_fields = ('parent_account__name', 'name')
    ordering = ('-created_at',)

    def get_parent_account_name(self, obj):
        return obj.parent_account.name if obj.parent_account else 'No Parent'
    get_parent_account_name.short_description = 'Parent Account'

