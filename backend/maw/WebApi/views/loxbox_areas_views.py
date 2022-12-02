import os 
import psutil 
import time 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from multiprocessing import Process
import psutil
import os 
from WebApi.models import LoxboxCities,LoxboxAreasSelectorProcess,Delegation,Locality
from WebApi.serializers import LoxboxCitiesSerializer,LoxboxAreasSelectorProcessSerializer
from WebApi.loxbox_areas_selectors_task import select_unselect_all_loxbox_areas,select_unselect_all_a_city,select_unselect_all_a_delegation
import time 


@api_view(['GET'])
def monitor_loxbox_areas_selector_process(request):
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    ser = LoxboxAreasSelectorProcessSerializer(loxbox_areas_selector_process_obj,many=False)
    return Response(ser.data,status=status.HTTP_200_OK)

@api_view(['GET'])
def loxbox_areas_list(request):
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    if loxbox_areas_selector_process_obj.is_working  :
        return Response(loxbox_areas_selector_process_obj.progress ,status = status.HTTP_200_OK)
    lx_cities_obj = LoxboxCities.objects.first()
    ser = LoxboxCitiesSerializer(lx_cities_obj,many=False)
    return Response(ser.data ,status = status.HTTP_200_OK)




@api_view(['PUT'])
def loxbox_areas_select_unselect_all(request,select_type):
    p = Process(target=select_unselect_all_loxbox_areas,kwargs={'is_select': True if select_type=='select_all' else False})  
    p.start()
    return Response({'msg':f'loxbox areas {select_type} was launched'},status = status.HTTP_200_OK)

@api_view(['PUT'])
def city_select_unselect_all(request,city_id,select_type):
    additional_action_beyond_the_main_action = request.data.get('additional_action_beyond_the_main_action')

    if additional_action_beyond_the_main_action == 'loxbox_areas_select_all' : 
        lx_cities = LoxboxCities.objects.first()
        lx_cities.selected_all = True 
        lx_cities.save()
    elif additional_action_beyond_the_main_action == 'loxbox_areas_disable_select_all' : 
        lx_cities = LoxboxCities.objects.first()
        lx_cities.selected_all = False 
        lx_cities.save()

    p = Process(target=select_unselect_all_a_city,args=(city_id,),kwargs={'is_select': True if select_type=='select_all' else False})  
    p.start()
    return Response({'msg':f'a {select_type} was launched on a city with id {city_id}'},status=status.HTTP_200_OK)

@api_view(['PUT'])
def delegation_select_unselect_all(request,delegation_id,select_type):
    additional_action_beyond_the_main_action = request.data.get('additional_action_beyond_the_main_action')
    match additional_action_beyond_the_main_action : 
        case 'loxbox_areas_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected_all = True 
            lx_cities.save() 
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected_all = True 
            city_obj.save()
        case 'loxbox_areas_disable_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected_all = False 
            lx_cities.save()
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected_all = False 
            city_obj.save()
        case 'city_select_all' :
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected_all = True 
            city_obj.save()
        case 'city_disable_select_all' :
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected_all = False 
            city_obj.save()
    p = Process(target=select_unselect_all_a_delegation,args=(delegation_id,),kwargs={'is_select': True if select_type=='select_all' else False})  
    p.start()
    return Response({'msg':f'a {select_type} was launched on a delegation with id {delegation_id}'},status=status.HTTP_200_OK)


@api_view(['PUT'])
def locality_select_unselect(request,locality_id,select_type):

    #SET selectected/unselected FOR THE loc_obj
    loc_obj = Locality.objects.get(id=locality_id)
    loc_obj.selected = True if select_type=='select' else False
    loc_obj.save()

    # HANDLE THE additional_action_beyond_the_main_action
    additional_action_beyond_the_main_action = request.data.get('additional_action_beyond_the_main_action')
    match additional_action_beyond_the_main_action : 
        case 'loxbox_areas_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected_all = True 
            lx_cities.save() 
            delegation_obj = loc_obj.delegation
            delegation_obj.selected_all = True 
            delegation_obj.save()
            delegation_obj.city.selected_all = True 
            delegation_obj.city.save()
        case 'loxbox_areas_disable_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected_all = False 
            lx_cities.save() 
            delegation_obj = loc_obj.delegation
            delegation_obj.selected_all = False 
            delegation_obj.save()
            delegation_obj.city.selected_all = False 
            delegation_obj.city.save()
        case 'city_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected_all = True 
            delegation_obj.save()
            delegation_obj.city.selected_all = True 
            delegation_obj.city.save()
        case 'city_disable_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected_all = False 
            delegation_obj.save()
            delegation_obj.city.selected_all = False 
            delegation_obj.city.save()
        case 'delegation_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected_all = True 
            delegation_obj.save()
        case 'delegation_disable_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected_all = False 
            delegation_obj.save()

    return Response({'msg':'success'},status=status.HTTP_200_OK)
