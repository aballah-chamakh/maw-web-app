import os 
import psutil 
import time 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from multiprocessing import Process
import psutil
import os 
from WebApi.models import OrderAction,LOADING_ORDERS
from OrderActionApi import grab_maw_orders

#pid = os.getpid()
#cmd = psutil.Process(pid).cmdline()
#if not(len(cmd) >= 3 and 'multiprocessing' in cmd[2]) : 

@api_view(['POST'])
def launch_orders_loader(request):
    days_ago = request.GET.get('days_ago') 
    if days_ago :
        days_ago = int(days_ago)
    else : 
        days_ago = 0 
    orders_loader_obj =  OrderAction.objects.create(type=LOADING_ORDERS)
    orders_loader_obj_id = orders_loader_obj.id
    p = Process(target=grab_maw_orders,args=(orders_loader_obj_id,),kwargs={'nb_of_days_ago':days_ago})
    p.start()
    print(f"ORDER LOADER ID : {orders_loader_obj_id}")
    return Response({'orders_loader_id':orders_loader_obj_id },status = status.HTTP_201_CREATED)


@api_view(['GET'])
def monitor_orders_loader(request,id):
    orders_loader_obj =  OrderAction.objects.get(id=id)
    return Response(orders_loader_obj.state,status=status.HTTP_200_OK)