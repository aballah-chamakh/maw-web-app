from rest_framework import serializers
from .models import AfexMonitorOrder,LoxboxMonitorOrder

"""
class AfexMonitorOrder(models.Model):
    order_id= models.IntegerField(unique=True)
    manifest_date = models.CharField(max_length=10)
    state = models.CharField(max_length=50)

class LoxboxMonitorOrder(models.Model):
    order_id= models.IntegerField(unique=True)
    transaction_id = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
"""
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