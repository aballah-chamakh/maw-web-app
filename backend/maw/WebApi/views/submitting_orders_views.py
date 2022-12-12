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
from OrderActionApi import submit_orders_to_carriers
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

    # GRAB THE ORDER LOADER OBJ
    orders_loader_obj = OrderAction.objects.get(id=orders_loader_id)

    # SEARCH FOR THE ORDER GIVEN HIS ID THEN TOOGLE HIS SELECT
    for order in orders_loader_obj.state['orders'] : 
        if order['id'] == order_id : 
            order['selected'] = not order['selected']
            break
        
    # SAVE THE ORDER LOADER OBJ
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

    # SEARCH FOR THE ORDER GIVEN HIS ID THEN UPDATE HIS CARRIER
    for order in orders_loader_obj.state['orders'] : 
        if order['id'] == order_id : 
            order['carrier'] = carrier
            break
    
    # SAVE THE ORDER LOADER OBJ
    orders_loader_obj.save()

    return Response({'res':'success' },status = status.HTTP_200_OK)

@api_view(['POST'])
def launch_orders_submitter(request):
    orders_loader_obj_id = request.data.get('orders_loader_id')
    orders_submitter_obj =  OrderAction.objects.create(type=SUBMITTING_ORDERS)
    p = Process(target=submit_orders_to_carriers,args=(orders_loader_obj_id,orders_submitter_obj.id,))
    p.start()
    return Response({'orders_submitter_id':orders_submitter_obj.id },status = status.HTTP_201_CREATED)


@api_view(['GET'])
def monitor_orders_submitter(request,id):
    orders_submitter_obj =  OrderAction.objects.get(id=id)
    return Response(orders_submitter_obj.state,status = status.HTTP_200_OK)

