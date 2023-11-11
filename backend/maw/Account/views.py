from django.shortcuts import render
from rest_framework import viewsets,mixins,status
from .models import CompanyProfile,CompanyOrderState
from .serializers import CompanyProfileSerializer,CompanyOrderStateSerializer
from .permissions import IsUserAuthenticatedAndAssociatedWithCompany
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response


class CompanyProfileViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin,mixins.UpdateModelMixin):
    serializer_class = CompanyProfileSerializer
    queryset = CompanyProfile.objects.all()  
    permission_classes = [IsUserAuthenticatedAndAssociatedWithCompany]

class CompanyOrderStateViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOrderStateSerializer
    queryset = CompanyOrderState.objects.all()
    permission_classes = [IsUserAuthenticatedAndAssociatedWithCompany]

    def perform_create(self,serializer):   
        current_company_profile_obj = self.request.user.companyprofile 
        serializer.save(company=current_company_profile_obj)

    def perform_update(self,serializer):   
        current_company_profile_obj = self.request.user.companyprofile 
        serializer.save(company=current_company_profile_obj)
           


