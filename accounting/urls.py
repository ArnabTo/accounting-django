from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountNameViewSet, AccountViewSet

router = DefaultRouter()
router.register(r'account-names', AccountNameViewSet)
router.register(r'accounts', AccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

