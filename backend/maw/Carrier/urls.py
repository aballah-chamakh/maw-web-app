from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CarrierViewSet, CarrierStateConversionViewSet


app_name = 'Carrier'
router = DefaultRouter()
router.register(r'carriers', CarrierViewSet)
router.register(r'carrier_state_conversions', CarrierStateConversionViewSet)

urlpatterns = [
    path('', include(router.urls))

]