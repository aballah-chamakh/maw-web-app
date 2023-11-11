from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet, CompanyOrderStateViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from .token import MyTokenObtainPairView

app_name = 'Account'
router = DefaultRouter()
router.register(r'companyprofiles', CompanyProfileViewSet)
router.register(r'company_order_states', CompanyOrderStateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]