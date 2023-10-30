from django.shortcuts import render

# Create your views here.

# carrier/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Carrier, CarrierStateConversion
from .serializers import CarrierSerializer, CarrierStateConversionSerializer,BulkActionSerializer

class CarrierViewSet(viewsets.ModelViewSet):
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer

    # THIS FUNCTION PERFORMS BULK ACTIONS ON CARRIER INSTANCES BASED ON REQUEST DATA
    # IT VALIDATES THE REQUEST DATA USING BulkActionSerializer AND HANDLES ACTIONS
    # SUCH AS ACTIVATING, DEACTIVATING, OR DELETING CARRIER INSTANCES.

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        # CREATE AN INSTANCE OF BulkActionSerializer TO VALIDATE REQUEST DATA
        ser = BulkActionSerializer(data=request.data)
        
        # IF THE SERIALIZER IS NOT VALID, RETURN A BAD REQUEST RESPONSE
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # EXTRACT 'action' AND 'carrier_ids' FROM THE VALIDATED DATA
        action = ser.data.get('action')
        carrier_ids = ser.data.get('carrier_ids')
        
        # FILTER CARRIER INSTANCES BASED ON THE LIST OF CARRIER IDS
        carriers_qs = Carrier.objects.filter(id__in=carrier_ids)
        
        # PERFORM ACTION BASED ON THE SPECIFIED 'action'
        if action == 'activate':
            # ACTIVATE CARRIER INSTANCES
            carriers_qs.update(active=True)
        elif action == 'deactivate':
            # DEACTIVATE CARRIER INSTANCES
            carriers_qs.update(active=False)
        else:
            # DELETE CARRIER INSTANCES IF 'action' IS NOT 'activate' OR 'deactivate'
            carriers_qs.delete()
        
        # RETURN A SUCCESS RESPONSE
        return Response({'res': 'success'}, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        carrier_state_conversions = request.data.pop('carrier_state_conversions', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        carrier = serializer.instance

        for conversion_data in carrier_state_conversions:
            CarrierStateConversion.objects.create(carrier=carrier, **conversion_data)

        headers = self.get_success_headers(serializer.data)
        return Response({'res': 'success'}, status=status.HTTP_201_CREATED, headers=headers)

class CarrierStateConversionViewSet(viewsets.ModelViewSet):
    queryset = CarrierStateConversion.objects.all()
    serializer_class = CarrierStateConversionSerializer

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        # Handle bulk delete of carrier state conversions
        # Use request.data to access the data sent in the request

        return Response({'res': 'success'}, status=status.HTTP_200_OK)

