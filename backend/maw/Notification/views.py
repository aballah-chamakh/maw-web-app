from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from Account.permissions import IsUserAuthenticatedAndAssociatedWithCompany
from .models import Notification 
from .serializers import NotificationSerializer 


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsUserAuthenticatedAndAssociatedWithCompany] #[IsUserAssociatedWithCompany]


    @action(detail=False, methods=['put'])
    def mark_as_read(self, request):
        # Get a list of notification IDs from the request data
        notification_ids = request.data.get('notification_ids', [])
        
        # Check if 'notification_ids' is missing or empty
        if not notification_ids:
            return Response({'error': 'notification_ids is missing or empty.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark the selected notifications as read
        notifications = Notification.objects.filter(id__in=notification_ids)
        for notification in notifications:
            notification.mark_as_read()
        
        return Response({'detail': 'Notifications marked as read.'}, status=status.HTTP_200_OK)
