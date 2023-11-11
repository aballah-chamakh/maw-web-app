from rest_framework import serializers
from .models import Notification 

class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    def get_created_at(self, obj):
        # Format the created_at field as "h:m:s dd/mm/yy"
        formatted_datetime = obj.created_at.strftime('%H:%M:%S %d/%m/%y')
        return formatted_datetime