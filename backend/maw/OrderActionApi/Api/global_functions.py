from .global_variables import LOXBOX_CITIES_DELEGATIONS, THE_BIG_TUNIS,LOXBOX_CARRIER_ID


def is_it_for_loxbox(city,delegation):
    if city in THE_BIG_TUNIS :
        #if delegation in LOXBOX_CITIES_DELEGATIONS[city] :
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