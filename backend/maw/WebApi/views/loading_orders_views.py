import os 
import psutil 
import time 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from multiprocessing import Process
import psutil
import os,sys
from WebApi.models import LoxboxAreasSelectorProcess,OrderAction,LOADING_ORDERS
from OrderActionApi.order_actions import grab_mawlety_orders
import subprocess

#pid = os.getpid()
#cmd = psutil.Process(pid).cmdline()
#if not(len(cmd) >= 3 and 'multiprocessing' in cmd[2]) : 

@api_view(['POST'])
def launch_orders_loader(request):

    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    if loxbox_areas_selector_process_obj.is_working  :
        return Response({'restriction_msg': 'ORDERS_LOADER_IS_DISABLED_NON'} ,status = status.HTTP_200_OK)

    date_range = request.data.get('date_range') 

    orders_loader_obj =  OrderAction.objects.create(type=LOADING_ORDERS,state={'state':'working','canceled':False})

    orders_loader_obj_id = orders_loader_obj.id
    subprocess.Popen([sys.executable,'-c',f'from OrderActionApi.order_actions import grab_mawlety_orders; grab_mawlety_orders({orders_loader_obj_id},{date_range})'])
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

@api_view(['GET'])
def get_last_undone_step_of_the_last_order_loader(request):
    last_orders_loader_obj = OrderAction.objects.filter(type=LOADING_ORDERS).last()
    undone_step = ""
    data = {'undone_step':undone_step}
    if last_orders_loader_obj : 
        orders_submitter_obj = last_orders_loader_obj.get_orders_submitter_obj()
        if last_orders_loader_obj.state['state'] == 'working' : 
            undone_step = "SHOW_ORDERS_LOADER_PROGRESS"
            data['orders_loader_id'] = last_orders_loader_obj.id 
        elif last_orders_loader_obj.state['canceled'] == False and last_orders_loader_obj.state.get('orders') and  orders_submitter_obj == None : 
            undone_step = "SHOW_ORDERS_TO_SUBMIT"
            data['orders_loader_id'] = last_orders_loader_obj.id 
        elif orders_submitter_obj and orders_submitter_obj.state['state'] == "working": 
            undone_step = "SHOW_ORDERS_SUBMITTER_PROGRESS"
            data['orders_loader_id'] = last_orders_loader_obj.id 
            data['orders_submitter_id'] = orders_submitter_obj.id 
        data['undone_step'] = undone_step 

    return Response(data,status=status.HTTP_200_OK)