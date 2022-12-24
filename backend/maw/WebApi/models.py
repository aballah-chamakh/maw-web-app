from django.db import models


LOADING_ORDERS = "LOADING_ORDERS"
SUBMITTING_ORDERS = "SUBMITTING_ORDERS"
MONITORING_ORDERS = "MONITORING_ORDERS"

def get_order_action_default_state(): 
    return {'state':'working'}
    

def get_lx_areas_selector_proc_default_state(): 
    return {'processed_items_cnt':0,'items_to_process_cnt':0}


class OrderAction(models.Model):
    type = models.CharField(max_length=50)
    state  = models.JSONField(default=get_order_action_default_state)

class AfexMonitorOrder(models.Model):
    order_id= models.IntegerField(unique=True)
    manifest_date = models.CharField(max_length=10)
    state = models.CharField(max_length=50)

class LoxboxMonitorOrder(models.Model):
    order_id= models.IntegerField(unique=True)
    transaction_id = models.CharField(max_length=255)
    state = models.CharField(max_length=50)

# LOXBOX AREAS MODELS 

class LoxboxAreasSelectorProcess(models.Model):
    is_working = models.BooleanField(default=False)
    progress = models.JSONField(default=get_lx_areas_selector_proc_default_state)


class LoxboxCities(models.Model):
    ALL_ELEMENTS_TO_BE_SELECTED_OR_UNSELECTED_COUNT = 5195 # CITIES COUNT + DELEGATIONS COUNT + LOCALITIES_COUNT + 1 OF THE LOXBOW CITIES OBJ (THE CONTAINER OF ALL OF THESE) 
    selected = models.BooleanField(default=False)
    
    def get_sub_address_level_elements(self) : 
         return self.city_set.all()
    
    def get_items_to_process_cnt(self,is_select):
        city_delg_loc_count = 0 
        city_qs = self.city_set.filter(selected=not is_select)
        city_delg_loc_count += city_qs.count()

        for city in city_qs : 
            delg_qs = city.delegation_set.filter(selected=not is_select)
            city_delg_loc_count += delg_qs.count()

            for delg in delg_qs : 
                city_delg_loc_count += delg.locality_set.filter(selected=not is_select).count()

        return city_delg_loc_count + 1 # CITIES COUNT + DELEGATIONS COUNT + LOCALITIES_COUNT + 1 OF THE LOXBOW CITIES OBJ (THE CONTAINER OF ALL OF THESE) 

class City(models.Model):
    loxbox_cities = models.ForeignKey(LoxboxCities,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    selected = models.BooleanField(default=False)

    def get_sub_address_level_elements(self) : 
         return self.delegation_set.all()

    def get_items_to_process_cnt(self,is_select): 
        delegations_qs = self.delegation_set.filter(selected=not is_select)
        delegations_count = delegations_qs.count()
        locs_count = 0 
        for delg_obj in delegations_qs : 
            locs_count += delg_obj.locality_set.filter(selected=not is_select).count()
        return delegations_count + locs_count + 1

class Delegation(models.Model):
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    selected = models.BooleanField(default=False)

    def get_sub_address_level_elements(self) : 
         return self.locality_set.all()

    def get_items_to_process_cnt(self,is_select): 
        return self.locality_set.filter(selected=not is_select).count()

class Locality(models.Model):
    delegation = models.ForeignKey(Delegation,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    selected = models.BooleanField(default=False)


    


