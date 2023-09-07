import os,sys
import psutil 
import time 
import subprocess
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from WebApi.models import LoxboxCities,LoxboxAreasSelectorProcess,Delegation,Locality
from WebApi.serializers import LoxboxCitiesSerializer,LoxboxAreasSelectorProcessSerializer
from WebApi.loxbox_areas_selectors_task import handle_loxbox_areas_long_select_or_deselect_task,get_address_level_element,handle_additional_action #,select_unselect_all_loxbox_areas,select_unselect_all_a_city,select_unselect_all_a_delegation

@api_view(['GET'])
def monitor_loxbox_areas_selector_process(request):
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    ser = LoxboxAreasSelectorProcessSerializer(loxbox_areas_selector_process_obj,many=False)
    return Response(ser.data,status=status.HTTP_200_OK)

@api_view(['GET'])
def loxbox_areas_list(request):
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    if loxbox_areas_selector_process_obj.is_working  :
        ser = LoxboxAreasSelectorProcessSerializer(loxbox_areas_selector_process_obj)
        return Response(ser.data ,status = status.HTTP_200_OK)
    lx_cities_obj = LoxboxCities.objects.first()
    ser = LoxboxCitiesSerializer(lx_cities_obj,many=False)
    return Response(ser.data ,status = status.HTTP_200_OK)


def init_loxbox_areas_selector_process() : 
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    loxbox_areas_selector_process_obj.is_working = True 
    loxbox_areas_selector_process_obj.progress = {'processed_items_cnt':0,'items_to_process_cnt':'XXX'}
    loxbox_areas_selector_process_obj.save()
    return loxbox_areas_selector_process_obj


@api_view(['PUT'])
def loxbox_areas_select_or_deselect(request):

    # GRAB THE REQUEST DATA 
    identifier = request.data.get('identifier')
    is_select = request.data.get('is_select')
    additional_action = request.data.get('additional_action')
    print(additional_action)

    # INIT LOXBOX AREAS SELECTOR PROCESS 
    loxbox_areas_selector_process_obj = init_loxbox_areas_selector_process()
    
    # SPLIT THE IDENTIFIER 
    splitted_identifier = identifier.split('_')

    # HANDLE THE LOCALITY WITHOUT LAUNCHING PROCESS BECAUSE WILL NOT TAKE TIME
    if len(splitted_identifier)  == 4  : 
        # GRAB THE ROOT ADDRESS LEVEL ELEMENT
        root_address_level_element = LoxboxCities.objects.first()

        # SELECT OR DESELECT THE LOCALITY
        locality_obj = get_address_level_element(root_address_level_element,splitted_identifier)
        locality_obj.selected = is_select
        locality_obj.save()

        # HANDLE ADDITIONAL ACTION
        if additional_action :
            handle_additional_action(root_address_level_element,splitted_identifier,additional_action,is_select)
        
        # FINISH THE THE LOXBOX SELECTOR PROCESS  
        loxbox_areas_selector_process_obj.is_working = False 
        loxbox_areas_selector_process_obj.save()
        
    else : # FOR THE OTHER ADDRESS LEVELS ABOVE THE LOCALITY LAUNCH A PROCESS
        # LAUNCH THE THE LOXBOX AREAS SELECTOR PROCESS
        arguments_data = {'splitted_identifier':splitted_identifier,'is_select' : is_select,'additional_action':additional_action}
        subprocess.Popen([sys.executable,'-c',f'from WebApi.loxbox_areas_selectors_task import handle_loxbox_areas_long_select_or_deselect_task; handle_loxbox_areas_long_select_or_deselect_task({arguments_data})'])

    return Response({'msg':f'THE LOBOX AREAS LONG SELECT OR DESELECT PROCESS WAS LAUNCHED'},status = status.HTTP_200_OK)






















# THE OLD VIEWS 

@api_view(['PUT']) 
def loxbox_areas_select_unselect_all(request,select_type):
    init_loxbox_areas_selector_process()
    p = Process(target=select_unselect_all_loxbox_areas,kwargs={'is_select': True if select_type=='select_all' else False})  
    p.start()
    return Response({'msg':f'loxbox areas {select_type} was launched'},status = status.HTTP_200_OK)

@api_view(['PUT'])
def city_select_unselect_all(request,city_id,select_type):
    init_loxbox_areas_selector_process()
    additional_action_beyond_the_main_action = request.data.get('additional_action_beyond_the_main_action')

    if additional_action_beyond_the_main_action == 'loxbox_areas_select_all' : 
        lx_cities = LoxboxCities.objects.first()
        lx_cities.selected = True 
        lx_cities.save()
    elif additional_action_beyond_the_main_action == 'loxbox_areas_disable_select_all' : 
        lx_cities = LoxboxCities.objects.first()
        lx_cities.selected = False 
        lx_cities.save()

    p = Process(target=select_unselect_all_a_city,args=(city_id,),kwargs={'is_select': True if select_type=='select_all' else False})  
    p.start()
    return Response({'msg':f'a {select_type} was launched on a city with id {city_id}'},status=status.HTTP_200_OK)

@api_view(['PUT'])
def delegation_select_unselect_all(request,delegation_id,select_type):
    init_loxbox_areas_selector_process()
    additional_action_beyond_the_main_action = request.data.get('additional_action_beyond_the_main_action')
    match additional_action_beyond_the_main_action : 
        case 'loxbox_areas_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected = True 
            lx_cities.save() 
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected = True 
            city_obj.save()
        case 'loxbox_areas_disable_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected = False 
            lx_cities.save()
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected = False 
            city_obj.save()
        case 'city_select_all' :
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected = True 
            city_obj.save()
        case 'city_disable_select_all' :
            city_obj = Delegation.objects.get(id=delegation_id).city
            city_obj.selected = False 
            city_obj.save()
    p = Process(target=select_unselect_all_a_delegation,args=(delegation_id,),kwargs={'is_select': True if select_type=='select_all' else False})  
    p.start()
    return Response({'msg':f'a {select_type} was launched on a delegation with id {delegation_id}'},status=status.HTTP_200_OK)


@api_view(['PUT'])
def locality_select_unselect(request,locality_id,select_type):
    init_loxbox_areas_selector_process()

    #SET selectected/unselected FOR THE loc_obj
    loc_obj = Locality.objects.get(id=locality_id)
    loc_obj.selected = True if select_type=='select' else False
    loc_obj.save()

    # HANDLE THE additional_action_beyond_the_main_action
    additional_action_beyond_the_main_action = request.data.get('additional_action_beyond_the_main_action')
    match additional_action_beyond_the_main_action : 
        case 'loxbox_areas_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected = True 
            lx_cities.save() 
            delegation_obj = loc_obj.delegation
            delegation_obj.selected = True 
            delegation_obj.save()
            delegation_obj.city.selected = True 
            delegation_obj.city.save()
        case 'loxbox_areas_disable_select_all' :
            lx_cities = LoxboxCities.objects.first()
            lx_cities.selected = False 
            lx_cities.save() 
            delegation_obj = loc_obj.delegation
            delegation_obj.selected = False 
            delegation_obj.save()
            delegation_obj.city.selected = False 
            delegation_obj.city.save()
        case 'city_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected = True 
            delegation_obj.save()
            delegation_obj.city.selected = True 
            delegation_obj.city.save()
        case 'city_disable_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected = False 
            delegation_obj.save()
            delegation_obj.city.selected = False 
            delegation_obj.city.save()
        case 'delegation_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected = True 
            delegation_obj.save()
        case 'delegation_disable_select_all' :
            delegation_obj = loc_obj.delegation
            delegation_obj.selected = False 
            delegation_obj.save()

    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    loxbox_areas_selector_process_obj.is_working = False 
    loxbox_areas_selector_process_obj.save()
    
    return Response({'msg':'success'},status=status.HTTP_200_OK)
