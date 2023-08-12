from .global_variables import LOXBOX_CITIES_DELEGATIONS, THE_BIG_TUNIS,LOXBOX_CARRIER_ID


def is_it_for_loxbox(city,delegation,locality):

    from WebApi.models import City 
    
    #CHECK IF THE CITY OF THE ORDER IS SELECTED WHICH MEAN THE LOCALITY IS AUTO SELECTED
    city_obj = City.objects.filter(name=city).first()
    
    if not city_obj :
        return False,['city','delgation','locality']

    #CHECK IF THE DELEGATION OF THE ORDER IS SELECTED WHICH MEAN THE LOCALITY IS AUTO SELECTED
    delegation_obj = city_obj.delegation_set.filter(name=delegation).first()
    if not delegation_obj : 
        return False,['delgation','locality']

    #CHECK IF THE LOCALITY OF THE ORDER IS SELECTED 
    locality_obj  = delegation_obj.locality_set.filter(name=locality).first()
    if locality_obj :
        if locality_obj.selected : 
            print('LOCALITY LEVEL')
            return True,[]
    else :
        return False,['locality']

    # RETURN FALSE IF NONE OF THE ONES BEFORE ARE TRUE 
    return False,[]


def split_selected_orders_between_loxbox_and_afex(orders):
    # INIT LOXBOX AND AFEX ORDERS 
    loxbox_orders = []
    afex_orders = []

    for order in orders : 
        
        # CHECK IF THE ORDER IS SELECTED TO APPEND IT 
        if not order['selected'] : 
            continue

        # CHECK IF THE ORDER IS FOR LOXBOX OTHERWISE HE IS FOR AFEX 
        if order['carrier'] == 'LOXBOX' :
            loxbox_orders.append(order)
        else :
            afex_orders.append(order)

    return loxbox_orders,afex_orders


def raise_a_unathorization_error(orders_action_obj,unathorization_error) :
    orders_action_obj.state['state'] = 'FINISHED'
    orders_action_obj.state['unauthorization_error'] = unathorization_error 
    orders_action_obj.save()
    quit() 
    

def raise_an_exception_error(orders_action_obj,exception_error) :
    orders_action_obj.state['state'] = 'FINISHED'
    orders_action_obj.state['exception_error'] = exception_error 
    orders_action_obj.save()
    quit() 


def raise_a_server_request_exception_error(orders_action_obj,exception_error) :
    orders_action_obj.state['state'] = 'FINISHED'
    orders_action_obj.state['server_request_exception_error'] = exception_error 
    orders_action_obj.save()
    quit() 
