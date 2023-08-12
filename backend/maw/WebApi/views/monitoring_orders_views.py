import os 
import psutil 
import time 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import subprocess 
from multiprocessing import Process
from WebApi.models import OrderAction,MONITORING_ORDERS,LoxboxMonitorOrder,AfexMonitorOrder
from WebApi.serializers import LoxboxMonitorOrderSerializer,AfexMonitorOrderSerializer
from OrderActionApi.order_actions import monitor_monitor_orders


@api_view(['POST'])
def launch_orders_monitoror(request):
    orders_monitoror_obj =  OrderAction.objects.create(type=MONITORING_ORDERS)
    #p = Process(target=monitor_monitor_orders,args=(orders_monitoror_obj.id,))
    subprocess.Popen(rf'C:\Users\chama\Desktop\maw\venv\Scripts\python.exe -c "from OrderActionApi.order_actions import monitor_monitor_orders ; monitor_monitor_orders({orders_monitoror_obj.id})" >> monitoring_orders.log',shell=True)
    print("done done")
    return Response({'orders_monitoror_id':orders_monitoror_obj.id },status = status.HTTP_201_CREATED)


@api_view(['GET'])
def monitor_orders_monitoror(request,id):
    orders_monitoror_obj =  OrderAction.objects.get(id=id)

    # IF THE ORDER MONITOROR IS FINISHED RETURN WITH HIS STATE THE LIST OF MONITOR ORDERS AFTER MONITORING
    if orders_monitoror_obj.state['state'] == "FINISHED" : 
        lx_monitor_orders = LoxboxMonitorOrder.objects.all()
        lx_ser = LoxboxMonitorOrderSerializer(lx_monitor_orders,many=True)

        fx_monitor_orders = AfexMonitorOrder.objects.all()
        fx_ser = AfexMonitorOrderSerializer(fx_monitor_orders,many=True)
    
        new_monitor_orders = lx_ser.data + fx_ser.data
        orders_monitoror_obj.state['new_monitor_orders'] = new_monitor_orders

    return Response(orders_monitoror_obj.state,status=status.HTTP_200_OK)


@api_view(['GET'])
def monitor_orders_list(request):
    # GRAB THE STATE OF THE LAST MONITOROR 
    last_monitoror = {'is_working':False}
    last_monitoror_obj = OrderAction.objects.filter(type=MONITORING_ORDERS).last()
    if last_monitoror_obj and last_monitoror_obj.state['state'] == 'working' : 
        last_monitoror['is_working'] = True 
        last_monitoror['orders_monitoror_id'] = last_monitoror_obj.id 

    # GRAB BOTH THE LOXBOX AND THE AFEX MONITOR ORDERS
    lx_monitor_orders = LoxboxMonitorOrder.objects.all()
    lx_ser = LoxboxMonitorOrderSerializer(lx_monitor_orders,many=True)

    fx_monitor_orders = AfexMonitorOrder.objects.all()
    fx_ser = AfexMonitorOrderSerializer(fx_monitor_orders,many=True)

    all_monitor_orders = lx_ser.data + fx_ser.data    
    return Response({'last_monitoror':last_monitoror,'all_monitor_orders':all_monitor_orders},status=status.HTTP_200_OK)