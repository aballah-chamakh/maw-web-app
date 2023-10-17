from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet, CompanyOrderStateViewSet

router = DefaultRouter()
router.register(r'companyprofiles', CompanyProfileViewSet)
router.register(r'companyorderstates', CompanyOrderStateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]