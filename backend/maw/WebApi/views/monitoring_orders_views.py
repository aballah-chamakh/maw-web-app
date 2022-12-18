import os 
import psutil 
import time 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from multiprocessing import Process
from WebApi.models import OrderAction,MONITORING_ORDERS,LoxboxMonitorOrder,AfexMonitorOrder
from WebApi.serializers import LoxboxMonitorOrderSerializer,AfexMonitorOrderSerializer
from OrderActionApi.order_actions import monitor_monitor_orders


@api_view(['POST'])
def launch_orders_monitoror(request):
    orders_monitoror_obj =  OrderAction.objects.create(type=MONITORING_ORDERS)
    p = Process(target=monitor_monitor_orders,args=(orders_monitoror_obj.id,))
    p.start()
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
    # GRAB BOTH THE LOXBOX AND THE AFEX MONITOR ORDERS
    lx_monitor_orders = LoxboxMonitorOrder.objects.all()
    lx_ser = LoxboxMonitorOrderSerializer(lx_monitor_orders,many=True)

    fx_monitor_orders = AfexMonitorOrder.objects.all()
    fx_ser = AfexMonitorOrderSerializer(fx_monitor_orders,many=True)


    all_monitor_order = lx_ser.data + fx_ser.data
    
    return Response(all_monitor_order,status=status.HTTP_200_OK)