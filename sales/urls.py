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

urlpatterns = [
    path('', include(router.urls)),
]
