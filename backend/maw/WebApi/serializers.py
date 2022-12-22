from rest_framework import serializers
from .models import AfexMonitorOrder,LoxboxMonitorOrder,LoxboxAreasSelectorProcess,LoxboxCities,City,Delegation,Locality


# MONITOR OREDERS SERIALIZERS 

class AfexMonitorOrderSerializer(serializers.ModelSerializer): 
    carrier = serializers.CharField(default='AFEX')
    class Meta: 
        model = AfexMonitorOrder
        fields = ['order_id','manifest_date','state','carrier']

class LoxboxMonitorOrderSerializer(serializers.ModelSerializer): 
    carrier = serializers.CharField(default='LOXBOX')
    class Meta: 
        model = LoxboxMonitorOrder
        fields = ['order_id','transaction_id','state','carrier']


# LOXBOX AREAS SERIALIZERS 

class LoxboxAreasSelectorProcessSerializer(serializers.ModelSerializer):
    class Meta: 
        model = LoxboxAreasSelectorProcess
        fields = ['is_working','progress']

class LoxboxCitiesSerializer(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()
    class Meta: 
        model = LoxboxCities
        fields = ['id','selected','cities']

    def get_cities(self,lx_cities_obj): 
        ser = CitySerializer(lx_cities_obj.city_set.all(),many=True)
        return ser.data

class CitySerializer(serializers.ModelSerializer):
    delegations = serializers.SerializerMethodField()

    class Meta: 
        model = City
        fields = ['id','name','selected','delegations']

    def get_delegations(self,city_obj): 
        ser = DelegationSerializer(city_obj.delegation_set.all(),many=True)
        return ser.data

class DelegationSerializer(serializers.ModelSerializer):
    localities = serializers.SerializerMethodField()

    class Meta: 
        model = Delegation
        fields = ['id','name','selected','localities']

    def get_localities(self,delg_obj): 
        ser = LocalitySerializer(delg_obj.locality_set.all(),many=True)
        return ser.data

class LocalitySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Locality
        fields = ['id','name','selected']


