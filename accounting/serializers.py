from rest_framework import serializers
from .models import AccountName, Account

class AccountNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountName
        fields = ['id', 'name', 'balance']

class AccountSerializer(serializers.ModelSerializer):
    parent_account = AccountNameSerializer(read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id',
            'account_type',
            'detail_type', 
            'name',
            'number',
            'parent_account',
            'balance',
            'as_of',
            'bank_name',
            'bank_account',
            'bank_routing',
            'bank_address',
            'description'
        ]
