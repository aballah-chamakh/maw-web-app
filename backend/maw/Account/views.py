from django.shortcuts import render
from rest_framework import viewsets  
from rest_framework import mixins 
from .models import CompanyProfile,CompanyOrderState
from .serializers import CompanyProfileSerializer,CompanyOrderStateSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class CompanyProfileViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin,mixins.UpdateModelMixin):
    serializer_class = CompanyProfileSerializer
    queryset = CompanyProfile.objects.all()
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return CompanyProfile.objects.get(user=user)
    """

class CompanyOrderStateViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOrderStateSerializer
    queryset = CompanyOrderState.objects.all()
    #permission_classes = [IsAuthenticated]


