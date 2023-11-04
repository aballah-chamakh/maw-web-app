from rest_framework import serializers
from .models import Carrier, CarrierStateConversion
from maw.CustomPagination import CustomPagination

class CarrierStateConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierStateConversion
        fields = '__all__'

class CarrierSerializer(serializers.ModelSerializer):
    carrier_state_conversions = serializers.SerializerMethodField(read_only=True)
    relative_logo = serializers.CharField(source='logo.url',read_only=True)
    logo = serializers.ImageField(write_only=True)
    name = serializers.CharField(read_only=True)
    paginator = CustomPagination() 

    class Meta:
        model = Carrier
        fields = '__all__'

    def get_carrier_state_conversions(self,carrier_obj):

        # SHOW THE CARRIER STATE CONVERSIONS ONLY ON THE RETREIVE ACTION 
        request  = self.context.get('request')   
        view = self.context.get('view')

        if not request or not view :
            return None

        if request.method != 'GET' or view.action != 'retrieve' : 
            return None 
        
        # GRAB THE CARRIER STATE CONVERSIONS OF ONLY THE CURRENT CARRIER  
        qs = carrier_obj.carrierstateconversion_set.all()

        # ADD PAGINATION TO THE RESULTS
        page = self.paginator.paginate_queryset(qs,request)
        ser = CarrierStateConversionSerializer(page,many=True)
        data = {
            'count' :  self.paginator.page.paginator.count,
            'next' : self.paginator.get_next_link(),
            'previous' : self.paginator.get_previous_link(),
            'results' : ser.data
        }

        # BECAUSE THE REQUEST IS FOR THE CARRIER WE NEED REPLACE 'carriers' BY 'carrierstateconversions' IN URLS OF THE PAGINATION
        if data['next'] : 
            data['next'] = data['next'].replace('carriers','carrierstateconversions')

        if data['previous'] : 
            data['previous'] = data['previous'].replace('carriers','carrierstateconversions')

        return data


class BulkActionSerializer(serializers.Serializer):
    ACTIONS = ('activate', 'deactivate')
    action = serializers.ChoiceField(choices=ACTIONS)
    carrier_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)


class BulkDeleteSerializer(serializers.Serializer):
    carrier_state_conversion_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
