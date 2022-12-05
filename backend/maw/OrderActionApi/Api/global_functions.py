from .global_variables import LOXBOX_CITIES_DELEGATIONS, THE_BIG_TUNIS,LOXBOX_CARRIER_ID


def is_it_for_loxbox(city,delegation,locality):
    from WebApi.models import City 
    
    #CHECK IF THE CITY OF THE ORDER IS SELECTED WHICH MEAN THE LOCALITY IS AUTO SELECTED
    city_obj = City.objects.filter(name=city).first()
    if city_obj.selected_all : 
        return True 

    #CHECK IF THE DELEGATION OF THE ORDER IS SELECTED WHICH MEAN THE LOCALITY IS AUTO SELECTED
    delegation_obj = city_obj.delegation_set.all().filter(name=delegation).first()
    if delegation_obj.selected_all : 
        return True 

    #CHECK IF THE LOCALITY OF THE ORDER IS SELECTED 
    locality_obj  = delegation_obj.locality_set.all().filter(name=locality).first()
    if locality_obj.selected : 
        return True 

    # RETURN FALSE IF NONE OF THE ONES BEFORE ARE TRUE 
    return False 


def split_orders_between_loxbox_and_afex(orders):
    # INIT LOXBOX AND AFEX ORDERS 
    loxbox_orders = []
    afex_orders = []

    for order in orders : 

        # GRAB CURRENT ORDER ADDRESS DATA  
        city = order['address_detail']['city']
        delegation = order['address_detail']['delegation']
        locality = order['address_detail']['locality']

        # CHECK IF THE ORDER IS FOR LOXBOX OTHERWISE HE IS FOR AFEX 
        if not delegation or not locality or is_it_for_loxbox(city,delegation,locality) :
            loxbox_orders.append(order)
        else :
            afex_orders.append(order)

            


    return loxbox_orders,afex_orders