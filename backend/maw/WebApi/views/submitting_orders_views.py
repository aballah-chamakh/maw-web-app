import os 
import psutil 
import time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from multiprocessing import Process
import psutil
import os 
from WebApi.models import LoxboxAreasSelectorProcess,OrderAction,SUBMITTING_ORDERS
from OrderActionApi.order_actions import submit_orders_to_carriers
import time 
#from OrderActionApi import grab_maw_orders

#pid = os.getpid()
#cmd = psutil.Process(pid).cmdline()
#if not(len(cmd) >= 3 and 'multiprocessing' in cmd[2]) : 

@api_view(['PUT'])
def toggle_order_selection(request):

    # GRAB THE REQUEST DATA
    # {orders_loader_id:33,order_id:1200}
    orders_loader_id = request.data.get('orders_loader_id')
    order_id = request.data.get('order_id')
    additional_action = request.data.get('additional_action')

    # GRAB THE ORDER LOADER OBJ
    orders_loader_obj = OrderAction.objects.get(id=orders_loader_id)
    orders_loader_obj.state['is_selector_working'] = True 
    orders_loader_obj.save() 

    # SEARCH FOR THE ORDER GIVEN HIS ID THEN TOOGLE HIS SELECT
    for order in orders_loader_obj.state['orders'] : 
        if order['id'] == order_id : 
            order['selected'] = not order['selected']
            break
    
    # HANDLE ADDITIONAL ACTION IF IT EXIST
    if additional_action : 
        if additional_action == 'selected_all' : 
            orders_loader_obj.state['orders_selected_all'] = True 
        else : 
            orders_loader_obj.state['orders_selected_all'] = False 

    # SAVE THE ORDER LOADER OBJ
    orders_loader_obj.state['is_selector_working'] = False
    orders_loader_obj.save()
    return Response({'res':'success' },status = status.HTTP_200_OK)

@api_view(['PUT'])
def select_unselect_all_orders(request):
    
    # GRAB THE REQUEST DATA
    orders_loader_id = request.data.get('orders_loader_id')
    action = request.data.get('action')
    print(action)
    is_selected = True if action == 'select_all' else False 

    # GRAB THE ORDER LOADER OBJ
    orders_loader_obj = OrderAction.objects.get(id=orders_loader_id)
    orders_loader_obj.state['is_selector_working'] = True 
    orders_loader_obj.save() 
  

    # SET THE STATE OF ALL ORDERS BASED ON THE ACTION
    orders_loader_obj.state['orders_selected_all'] = is_selected 
    
    # SET THE STATE OF EACH ORDER BASED ON THE ACTION
    for order in orders_loader_obj.state['orders'] : 
        order['selected'] = is_selected
        
    # SAVE THE ORDER LOADER OBJ
    orders_loader_obj.state['is_selector_working'] = False
    orders_loader_obj.save()
    return Response({'res':'success' },status = status.HTTP_200_OK)

@api_view(['PUT'])
def set_order_carrier(request):

    # GRAB THE REQUEST DATA
    # {orders_loader_id:33,order_id:1200,carrier:'AFEX'}
    orders_loader_id = request.data.get('orders_loader_id')
    order_id = request.data.get('order_id')
    carrier = request.data.get('carrier')

    # GRAB THE ORDER LOADER OBJ
    orders_loader_obj = OrderAction.objects.get(id=orders_loader_id)
    orders_loader_obj.state['is_selector_working'] = True 
    orders_loader_obj.save() 

    # SEARCH FOR THE ORDER GIVEN HIS ID THEN UPDATE HIS CARRIER
    for order in orders_loader_obj.state['orders'] : 
        if order['id'] == order_id : 
            order['carrier'] = carrier
            break
    
    # SAVE THE ORDER LOADER OBJ
    orders_loader_obj.state['is_selector_working'] = False
    orders_loader_obj.save()

    return Response({'res':'success' },status = status.HTTP_200_OK)

@api_view(['POST'])
def launch_orders_submitter(request):
    orders_loader_obj_id = int(request.data.get('orders_loader_id'))
    orders_submitter_obj =  OrderAction.objects.create(type=SUBMITTING_ORDERS,state={'state':'working','orders_loader_id':orders_loader_obj_id})
    p = Process(target=submit_orders_to_carriers,args=(orders_submitter_obj.id,))
    p.start()
    return Response({'orders_submitter_id':orders_submitter_obj.id },status = status.HTTP_201_CREATED)


@api_view(['GET'])
def monitor_orders_submitter(request,id):
    orders_submitter_obj =  OrderAction.objects.get(id=id)
    return Response(orders_submitter_obj.state,status = status.HTTP_200_OK)

