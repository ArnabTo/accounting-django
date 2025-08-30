from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Account, AccountName
from .serializers import AccountSerializer, AccountNameSerializer

class AccountNameViewSet(viewsets.ModelViewSet):
    queryset = AccountName.objects.all()
    serializer_class = AccountNameSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer