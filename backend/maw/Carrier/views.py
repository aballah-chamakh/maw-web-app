# carrier/views.py
from rest_framework import viewsets, status , mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from Account.permissions import IsUserAuthenticatedAndAssociatedWithCompany
from .models import Carrier, CarrierStateConversion
from .serializers import (CarrierSerializer, CarrierStateConversionSerializer,
                          BulkActionSerializer,BulkDeleteSerializer)


class CarrierViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer

    permission_classes = [IsUserAuthenticatedAndAssociatedWithCompany] #[IsUserAssociatedWithCompany]

    # THIS FUNCTION PERFORMS BULK ACTIONS ON CARRIER INSTANCES BASED ON REQUEST DATA
    # IT VALIDATES THE REQUEST DATA USING BulkActionSerializer AND HANDLES ACTIONS
    # SUCH AS ACTIVATING, DEACTIVATING, OR DELETING CARRIER INSTANCES.

    @action(detail=False, methods=['patch'])
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



class CarrierStateConversionViewSet(mixins.ListModelMixin,
                                    mixins.CreateModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.GenericViewSet):

    queryset = CarrierStateConversion.objects.all()
    serializer_class = CarrierStateConversionSerializer
    permission_classes = [IsUserAuthenticatedAndAssociatedWithCompany]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filtering based on the query parameter carrier_id
        query_param_carrier_id = self.request.query_params.get('carrier_id')
        if query_param_carrier_id :
            queryset = queryset.filter(carrier=query_param_carrier_id)

        return queryset

    def list(self, request, *args, **kwargs):
        # Get the value of the query parameter carrier_id
        query_param_carrier_id = request.query_params.get('carrier_id')

        # If the query parameter carrier_id is None, respond with a 400 Bad Request
        if query_param_carrier_id is None :
            return Response(
                {'detail': 'The "carrier_id" query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().list(self, request, *args, **kwargs)

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        # Handle bulk delete of carrier state conversions
        # Use request.data to access the data sent in the request
                # CREATE AN INSTANCE OF BulkActionSerializer TO VALIDATE REQUEST DATA
        ser = BulkDeleteSerializer(data=request.data)
        
        # IF THE SERIALIZER IS NOT VALID, RETURN A BAD REQUEST RESPONSE
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        
        carrier_state_conversion_ids = ser.data.get('carrier_state_conversion_ids')
        carriers_qs = Carrier.objects.filter(id__in=carrier_state_conversion_ids)

        carriers_qs.delete()

        return Response({'res': 'success'}, status=status.HTTP_200_OK)



