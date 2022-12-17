



# SUBMIT ORDERS TO CARRIERS 

def submit_orders_to_carriers(orders_loader_id,orders_submitter_id):
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

    # GRAB THE ORDERS FROM THE ORDER LOADER 
    #order_loader_obj = OrderAction.objects.get(id=orders_loader_id)
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
    #orders = order_loader_obj.state['orders']

    # SPLIT ORDERS BETWEEN AFEX AND LOXBOX
    loxbox_orders,afex_orders = split_selected_orders_between_loxbox_and_afex(orders)

    # SUBMIT THE ORDERS TO THEIR CARRIERS WHILE SAVING THE PROGRESS OF SUBMITTING THE ORDERS IN THE orders_submitter_obj
    orders_submitter_obj = OrderAction.objects.get(id=orders_submitter_id)

    if len(loxbox_orders) > 0 :  

        # SET THE INITIAL DATA OF THE PROGRESS OF THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress'] = {'current_order_id' : loxbox_orders[0]['id'] ,'submitted_orders_len' :  0,'orders_to_be_submitted': len(loxbox_orders)+len(afex_orders)} 
        orders_submitter_obj.save()

        submit_loxbox_orders(loxbox_orders,orders_submitter_obj,add_loxbox_order_to_monitoring_phase) 

    if len(afex_orders) > 0 : 

        # SET THE INITIAL DATA OF THE PROGRESS OF THE ORDERS SUBMITTER
        if not orders_submitter_obj.state.get('progress') :
            orders_submitter_obj.state['progress'] = {'current_order_id' : afex_orders[0]['id'] ,'submitted_orders_len' :  0,'orders_to_be_submitted': len(afex_orders)} 
        else : 
            orders_submitter_obj.state['progress']['current_order_id'] = afex_orders[0]['id']

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

    # IMPORTS 
    from WebApi.models import OrderAction,AfexMonitorOrder,LoxboxMonitorOrder
    from .Api.monitoring_API import update_a_monitor_order_by_id,delete_a_monitor_order_by_id
    from .Api.loxbox_API import update_monitor_orders_state_from_loxbox
    from .Api.afex_API import update_afex_monitor_orders_state_from_afex

    # GRAB  orders_monitoror_obj WHERE WE GONA RECORD THE PREGRESS OF THE MONITOREING AND EVENTUALLY THE RESUTLS
    orders_monitoror_obj = OrderAction.objects.get(id=orders_monitoror_id)

    # GRAB BOTH THE LOXBOX AND THE AFEX MONITOR ORDERS
    lx_monitor_orders = LoxboxMonitorOrder.objects.all()
    fx_monitor_orders = AfexMonitorOrder.objects.all()

    # MONITOR LOXBOX MONITOR ORDERS
    if len(lx_monitor_orders) > 0 : 
        
        # SET THE INITIAL DATA OF THE PROGRESS OF THE ORDERS MONITOROR
        orders_monitoror_obj.state['progress'] = {'current_order_id' : lx_monitor_orders.first().order_id ,'submitted_orders_len' :  0,'orders_to_be_monitored': lx_monitor_orders.count()+fx_monitor_orders.count()} 
        orders_monitoror_obj.save()

        update_monitor_orders_state_from_loxbox(lx_monitor_orders,update_a_monitor_order_by_id,delete_a_monitor_order_by_id,orders_monitoror_obj=orders_monitoror_obj)
    
    # MONITOR AFEX MONITOR ORDERS
    if len(fx_monitor_orders) > 0 : 

        if orders_monitoror_obj.state.get('monitored_orders_len') == None  : 
            orders_monitoror_obj.state['monitored_orders_len'] = 0 

        orders_monitoror_obj.state['current_order_id'] = fx_monitor_orders[0].order_id
        orders_monitoror_obj.save()

        if not orders_monitoror_obj.state.get('progress') :
            orders_monitoror_obj.state['progress'] = {'current_order_id' : fx_monitor_orders.first().order_id ,'submitted_orders_len' :  0,'orders_to_be_monitored': fx_monitor_orders.count()} 
            orders_monitoror_obj.save()
        else : 
            orders_monitoror_obj.state['progress']['current_order_id'] = fx_monitor_orders.first().order_id 

        update_afex_monitor_orders_state_from_afex(fx_monitor_orders,orders_monitoror_obj)

    orders_monitoror_obj.state['state'] = "FINISHED"
    orders_monitoror_obj.save()

    


