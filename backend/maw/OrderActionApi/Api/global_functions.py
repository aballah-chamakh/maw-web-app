from .global_variables import LOXBOX_CITIES_DELEGATIONS, THE_BIG_TUNIS,LOXBOX_CARRIER_ID


def is_it_for_loxbox(city,delegation,locality):
    from WebApi.models import City 
    city_obj = City.objects.filter(name=city).first()
    if city_obj.selected_all : 
        return True 
    delegation_obj = city_obj.delegation_set.all().filter(name=delegation).first()
    if delegation_obj.selected_all : 
        return True 
    locality_obj  = delegation_obj.locality_set.all().filter(name=locality).first()
    if locality_obj.selected : 
        return True 
    return False 


def split_orders_between_loxbox_and_afex(orders):
    loxbox_orders = []
    afex_orders = []
    for order in orders : 
        if order['id_carrier'] == LOXBOX_CARRIER_ID or is_it_for_loxbox(order['address_detail']['city'],order['address_detail']['delegation']) :
            loxbox_orders.append(order)
        else :
            afex_orders.append(order)
    return loxbox_orders,afex_orders