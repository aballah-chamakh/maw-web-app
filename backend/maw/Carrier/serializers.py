from rest_framework import serializers
from .models import Carrier, CarrierStateConversion

class CarrierStateConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierStateConversion
        fields = '__all__'

class CarrierSerializer(serializers.ModelSerializer):
    carrier_state_conversions = CarrierStateConversionSerializer(many=True, required=False)

    class Meta:
        model = Carrier
        fields = '__all__'


class BulkActionSerializer(serializers.Serializer):
    ACTIONS = ('delete', 'activate', 'deactivate')
    action = serializers.ChoiceField(choices=ACTIONS)
    carrier_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)