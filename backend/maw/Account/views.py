from django.shortcuts import render
from rest_framework import viewsets,mixins,status
from .models import CompanyProfile,CompanyOrderState
from .serializers import CompanyProfileSerializer,CompanyOrderStateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response



# Create your views here.
def generate_random_name():
    import random
    prefixes = ['Ad', 'Be', 'Co', 'Di', 'Em', 'Fo', 'Ga', 'He', 'I', 'Jo', 'Ki', 'La', 'Me', 'No', 'O', 'Pa', 'Qu', 'Re', 'Si', 'To', 'U', 'Vi', 'Wa', 'Xa', 'Y', 'Ze']
    middle_parts = ['l', 'm', 'n', 'r', 's', 't', 'v', 'w', 'z']
    suffixes = ['a', 'e', 'i', 'o', 'u', 'y']
    prefix = random.choice(prefixes)
    middle = random.choice(middle_parts)
    suffix = random.choice(suffixes)
    name = prefix + middle + suffix
    print(name)
    return name

class CompanyProfileViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin,mixins.UpdateModelMixin):
    serializer_class = CompanyProfileSerializer
    queryset = CompanyProfile.objects.all()
    anyx = generate_random_name()

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

    #def get_queryset(self,request) : 
    #    return CompanyOrderState.objects.all().filter(company = company


