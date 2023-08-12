import datetime
import sqlite3

from .loxbox_API import update_monitor_orders_state_from_loxbox
#from afex_API import update_afex_monitor_orders_state_from_afex
from .global_variables import DELETE_MONITOR_ORDER_STATES, AFEX_MONITOR_ORDER_TABLE_NAME,LOXBOX_MONITOR_ORDER_TABLE_NAME
from .mawlety_API import update_order_state_in_mawlety
from WebApi.models import AfexMonitorOrder,LoxboxMonitorOrder



 

def create_a_monitor_order(monitor_order,carrier): 
    if carrier == 'AFEX' : 
        AfexMonitorOrder.objects.create(**monitor_order)
    else : 
        LoxboxMonitorOrder.objects.create(**monitor_order)


def delete_a_monitor_order_by_id(carrier,order_id):
    if carrier == 'AFEX' : 
        AfexMonitorOrder.objects.get(order_id=order_id).delete()
    else : 
        LoxboxMonitorOrder.objects.get(order_id=order_id).delete()

def update_a_monitor_order_by_id(carrier,order_id,new_state):
    if carrier == 'AFEX' : 
        afex_monitor_order_obj = AfexMonitorOrder.objects.get(order_id=order_id)
        afex_monitor_order_obj.state = new_state
        afex_monitor_order_obj.save()
    else : 
        loxbox_monitor_order_obj = LoxboxMonitorOrder.objects.get(order_id=order_id)
        loxbox_monitor_order_obj.state = new_state
        loxbox_monitor_order_obj.save()



def add_loxbox_order_to_monitoring_phase(order):
    #CREATE THE INITIAL ROW OF THE MONITOR ORDER
    monitor_order = {'order_id':order['id'],'transaction_id': str(order['transaction_id']) ,'state':'En cours de préparation'}

    # CREATE THE MONITOR_ORDER TABLE IN DB 
    create_a_monitor_order(monitor_order,"LOXBOX")
    
    #SET THE ORDER STATE IN MAWLETY.COM TO "En cours de préparation" 
    #update_order_state_in_mawlety(monitor_order['order_id'],monitor_order['state']) 

    # TRASH CODE 
    # HANDLE THE CASE OF THE ORDER WAS CREATED BY THE MODULE OF LOXBOX , CHECK IF FATMA FORGET TO RUN OUR PROG AND THE STATE OF THE ORDER WAS UPDATED IN LOXBOX
    # NOTE :  IF TRANSACTION ID NOT FALSE IN THE ORDER IT MEAN THAT THE ORDER WAS CREATED BY THE LOXBOX MODULE
    #if already_created :
    #    monitor_order = update_monitor_orders_state_from_loxbox([monitor_order],update_a_monitor_order_by_id,delete_a_monitor_order_by_id,return_monitor_orders_updated=True)[0]
    


    
    # IF THE STATE OF MONITOR ORDER EQUAL TO A STATE OTHER THAN 'En cours de préparation' WE DO NOTHING 
    # BECAUSE update_monitor_orders_state_from_loxbox WILL DO THE JOBEn cours de préparation
    #if monitor_order['state'] == 'En cours de préparation':  
    


def add_afex_order_to_monitoring_phase(order) : 
    monitor_order = {'order_id':order['id'],'state':'En cours de préparation','barcode':order['barcode']}
    create_a_monitor_order(monitor_order,"AFEX")
    






























    




        

"""
monitor_order = {'order_id':int("444"),'transaction_id':int("333333333333333333") ,'state':'En cours de préparation','carrier':'loxbox'}

orders = get_all_monitor_orders()
for order in orders : 
    print(order)
create_a_monitor_order(monitor_order)
update_a_monitor_order_by_id(monitor_order['order_id'],'Expédié')
delete_a_monitor_order_by_id(88)
orders = get_all_monitor_orders()
for order in orders : 
    print(order)




"""
