import os 
import psutil 
import time 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from multiprocessing import Process
import psutil
import os 
from WebApi.models import LoxboxAreasSelectorProcess,OrderAction,LOADING_ORDERS
from OrderActionApi import grab_maw_orders

#pid = os.getpid()
#cmd = psutil.Process(pid).cmdline()
#if not(len(cmd) >= 3 and 'multiprocessing' in cmd[2]) : 

@api_view(['POST'])
def launch_orders_loader(request):
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    if loxbox_areas_selector_process_obj.is_working  :
        return Response({'restriction_msg': 'ORDERS_LOADER_IS_DISABLED_NON'} ,status = status.HTTP_200_OK)

    print(request.data.keys())
    days_ago = request.data.get('days_ago') 
    if days_ago :
        days_ago = int(days_ago)
    else : 
        days_ago = 0 
    orders_loader_obj =  OrderAction.objects.create(type=LOADING_ORDERS)

    # INITIATE THE CANCEL STATE FOR THE ORDER LOADER 
    orders_loader_obj.state['canceled'] = False 
    orders_loader_obj.save()

    orders_loader_obj_id = orders_loader_obj.id
    p = Process(target=grab_maw_orders,args=(orders_loader_obj_id,),kwargs={'nb_of_days_ago':days_ago})
    p.start()
    print(f"ORDER LOADER ID : {orders_loader_obj_id}")
    return Response({'orders_loader_id':orders_loader_obj_id },status = status.HTTP_201_CREATED)

@api_view(['PUT'])
def cancel_orders_loader(request,id):
    orders_loader_obj =  OrderAction.objects.get(id=id)
    orders_loader_obj.state['canceled'] = True 
    orders_loader_obj.save()
    return Response({'msg':'success'},status=status.HTTP_200_OK)

@api_view(['GET'])
def monitor_orders_loader(request,id):
    orders_loader_obj =  OrderAction.objects.get(id=id)
    return Response(orders_loader_obj.state,status=status.HTTP_200_OK)