from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Notification.views import NotificationViewSet

app_name = 'Notification'

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)


urlpatterns = [
    path('', include(router.urls)),
]