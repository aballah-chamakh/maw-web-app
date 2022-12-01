from django.db import models


LOADING_ORDERS = "LOADING_ORDERS"
SUBMITTING_ORDERS = "SUBMITTING_ORDERS"
MONITORING_ORDERS = "MONITORING_ORDERS"

def get_default_state(): 
    x = {'state':'working'}
    print(id(x))
    return x

class OrderAction(models.Model):
    type = models.CharField(max_length=50)
    state  = models.JSONField(default=get_default_state)

class AfexMonitorOrder(models.Model):
    order_id= models.IntegerField(unique=True)
    manifest_date = models.CharField(max_length=10)
    state = models.CharField(max_length=50)

class LoxboxMonitorOrder(models.Model):
    order_id= models.IntegerField(unique=True)
    transaction_id = models.CharField(max_length=255)
    state = models.CharField(max_length=50)

# LOXBOX AREAS MODELS 

class LoxboxCities(models.Model):
    selected_all = models.BooleanField(default=False)

class City(models.Model):
    loxbox_cities = models.ForeignKey(LoxboxCities,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    selected_all = models.BooleanField(default=False)

class Delegation(models.Model):
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    selected_all = models.BooleanField(default=False)

class Locality(models.Model):
    delegation = models.ForeignKey(Delegation,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    selected = models.BooleanField(default=False)


    


