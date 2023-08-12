



# SUBMIT ORDERS TO CARRIERS 

import time

# THIS ADDITONNAL FUNCTION IS A WRAPPER TO NOT LOAD DJANGO MODELS BEFORE THE DJANGO ENV IS LOADED IN THE NEW 
# PROCESS 

def grab_mawlety_orders(orders_loader_obj_id,date_range): 
    import django
    import os 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    from .Api.mawlety_API import grab_maw_orders
    grab_maw_orders(orders_loader_obj_id,date_range)


def submit_orders_to_carriers(orders_submitter_id):
    # LOAD THE DJANGO ENV
    import django
    import os 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    from WebApi.models import OrderAction
    from .Api.monitoring_API import add_loxbox_order_to_monitoring_phase
    from .Api.loxbox_API import submit_loxbox_orders
    from .Api.afex_API import submit_afex_orders
    from .Api.global_functions import split_selected_orders_between_loxbox_and_afex

    """
    orders = []
    for i in range(514,520):
        orders.append(
            {
            'id': i, 
            'id_carrier': '91',
            'transaction_id': False, 
            'address_detail': {'city': 'Tunis' if i % 2 == 0 else 'Gabes', 'delegation': 'La Marsa' if i % 2 == 0 else 'El Hamma', 'locality': 'Jardins de Carthage' if i % 2 == 0 else 'Bechima',
            'address1': 'résidence Aziz  Jardins de Carthage', 'phone_mobile': '98482121'}, 
            'customer_detail': {'firstname': 'test', 'lastname': 'test', 'email': 'test@yahoo.fr'}, 
            'cart_products': [{'name': 'TRIO DEFINISSEUR BOUCLES', 'quantity': '1'}],
            'total_paid': '105.300000',
            'selected' :  True
            }
        )
    """
    orders_submitter_obj = OrderAction.objects.get(id=orders_submitter_id)
    
    # GRAB THE ORDERS FROM THE ORDER LOADER 
    order_loader_obj = OrderAction.objects.get(id=orders_submitter_obj.state['orders_loader_id'])
    orders = order_loader_obj.state['orders']

    # SPLIT THE SELECTED ORDERS BETWEEN AFEX AND LOXBOX
    loxbox_orders,afex_orders = split_selected_orders_between_loxbox_and_afex(orders)

    # SUBMIT THE ORDERS TO THEIR CARRIERS WHILE SAVING THE PROGRESS OF SUBMITTING THE ORDERS IN THE orders_submitter_obj
    

    if len(loxbox_orders) > 0 :  

        # SET THE INITIAL DATA OF THE PROGRESS OF THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress'] = {'current_order_id' : loxbox_orders[0]['id'] ,'submitted_orders_len' :  0,'orders_to_be_submitted': len(loxbox_orders)+len(afex_orders),'carrier':'LOXBOX'} 
        orders_submitter_obj.save()

        submit_loxbox_orders(loxbox_orders,orders_submitter_obj,add_loxbox_order_to_monitoring_phase) 

    if len(afex_orders) > 0 : 

        # SET THE INITIAL DATA OF THE PROGRESS OF THE ORDERS SUBMITTER
        if not orders_submitter_obj.state.get('progress') :
            orders_submitter_obj.state['progress'] = {'current_order_id' : afex_orders[0]['id'] ,'submitted_orders_len' :  0,'orders_to_be_submitted': len(afex_orders),'carrier':'AFEX'}
            orders_submitter_obj.save()
        else : 
            orders_submitter_obj.state['progress']['current_order_id'] = afex_orders[0]['id']
            orders_submitter_obj.state['progress']['carrier'] = 'AFEX'
            orders_submitter_obj.save()

        submit_afex_orders(afex_orders,orders_submitter_obj)

    # SET THE FINISH STATE TO THE ORDERS SUBMITTER
    orders_submitter_obj.state['state'] = "FINISHED"
    orders_submitter_obj.save()
    



def monitor_monitor_orders(orders_monitoror_id) : 
    # LOAD THE DJANGO ENV
    import django
    import os 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    time.sleep(20)

    # IMPORTS 
    from WebApi.models import OrderAction,AfexMonitorOrder,LoxboxMonitorOrder
    from .Api.monitoring_API import update_a_monitor_order_by_id,delete_a_monitor_order_by_id
    from .Api.loxbox_API import update_monitor_orders_state_from_loxbox
    from .Api.afex_API import update_afex_monitor_orders_state_from_afex

    print('TEST THE MONITORING LOGS ...')

    # GRAB  orders_monitoror_obj WHERE WE GONA RECORD THE PREGRESS OF THE MONITOREING AND EVENTUALLY THE RESUTLS
    orders_monitoror_obj = OrderAction.objects.get(id=orders_monitoror_id)


    # GRAB BOTH THE LOXBOX AND THE AFEX MONITOR ORDERS
    lx_monitor_orders = LoxboxMonitorOrder.objects.all()
    fx_monitor_orders = AfexMonitorOrder.objects.all()

    # INITIATE THE results AND THE conv_errors KEYS INTO THE STATES 
    orders_monitoror_obj.state['results'] = []
    orders_monitoror_obj.state['conv_errors'] = {}

    # MONITOR LOXBOX MONITOR ORDERS
    if len(lx_monitor_orders) > 0: 
        # INITIATE CONV ERRORS FOR LOXBOX 
        orders_monitoror_obj.state['conv_errors'] = {'LOXBOX':{}}
        
        # SET THE INITIAL PROGRESS DATA OF LOXBOX
        orders_monitoror_obj.state['progress'] = {'current_order_id' : lx_monitor_orders.first().order_id ,'monitored_orders_len' :  0,'orders_to_be_monitored': lx_monitor_orders.count()+fx_monitor_orders.count(),'carrier':'LOXBOX'} 
        
        orders_monitoror_obj.save()

        update_monitor_orders_state_from_loxbox(lx_monitor_orders,orders_monitoror_obj,update_a_monitor_order_by_id,delete_a_monitor_order_by_id)
    
    # MONITOR AFEX MONITOR ORDERS
    if len(fx_monitor_orders) > 0 :
        
        # SET THE INTITAL PROGRESS DATA OF AFEX 
        if not orders_monitoror_obj.state.get('progress') :
            orders_monitoror_obj.state['progress'] = {'current_order_id' : fx_monitor_orders.first().order_id ,'monitored_orders_len' :  0,'orders_to_be_monitored': fx_monitor_orders.count(),'carrier':'AFEX'} 
        else : 
            orders_monitoror_obj.state['progress']['current_order_id'] = fx_monitor_orders.first().order_id 
            orders_monitoror_obj.state['progress']['carrier'] = 'AFEX'
        # INITIATE CONV ERRORS FOR AFEX 
        orders_monitoror_obj.state['conv_errors']['AFEX'] = {}
    
        orders_monitoror_obj.save()
       

        update_afex_monitor_orders_state_from_afex(fx_monitor_orders,orders_monitoror_obj)

    orders_monitoror_obj.state['state'] = "FINISHED"
    orders_monitoror_obj.save()

    


