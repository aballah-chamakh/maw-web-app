

def log_loxbox_areas_selector_process_progress(loxbox_areas_selector_process_obj,is_finished=False,processed_items_log_interval=20):
    if is_finished or loxbox_areas_selector_process_obj.progress['processed_items_cnt'] % processed_items_log_interval == 0 : 
        if is_finished : 
            loxbox_areas_selector_process_obj.is_working = False 
        loxbox_areas_selector_process_obj.save()


def get_address_level_element(root_address_level_element,splitted_identifier) :
    address_level_element = root_address_level_element
    for idx,current_address_level_idx in enumerate(splitted_identifier) : 
        # SKIP THE FIRST ADDRESS LEVEL IDX BECAUSE HIS ADDRESS LEVEL ELEMENT IS THE SAME AS THE INITIAL ONE 
        if idx != 0 : 
            # CURRENT  ADDR LVL ELEMENT = PREVIOUS ADDR LVL ELEMENT . HIS SUB ELEMENTS [THE CURRENT ADRRESS LEVEL IDX OF THE IDENTIFIER]
            address_level_element = address_level_element.get_sub_address_level_elements()[int(current_address_level_idx)]
    return address_level_element

def select_or_deselect_address_level_element_recursively(address_level_element,is_select,loxbox_areas_selector_process_obj):
    # SELECT OR DESELECT THE address_level_element
    address_level_element.selected = is_select 
    address_level_element.save()
    
    # LOG THE PROGRESS OF THE SELECT OR DESELECT 
    loxbox_areas_selector_process_obj.progress['processed_items_cnt'] += 1 
    log_loxbox_areas_selector_process_progress(loxbox_areas_selector_process_obj)

    # BREAK THE RECURSIVITY WHEN A THE address_level_element IS A LOCALITY OBJECT
    if address_level_element.__class__.__name__ == 'Locality' : 
        return 
    
    # SELECT OR DESELECT THE SUB ADDRESS LEVEL ELEMENTS OF THE CURRENT ONE 
    for sub_address_level_element in address_level_element.get_sub_address_level_elements().filter(selected=not is_select) : 
        select_or_deselect_address_level_element_recursively(sub_address_level_element,is_select,loxbox_areas_selector_process_obj)

def handle_additional_action(root_address_level_element,splitted_identifier,additional_action,is_select): 
    address_levels = ['loxbox_areas','city','delegation','locality']

    # SET THE first_idx_range THE INDEX OF THE ADDRESS LEVEL OF THE ADDITIONAL ACTION
    additional_action_address_level = additional_action.replace('_select_all','').replace('_disable','')
    first_idx_range = address_levels.index(additional_action_address_level)
    
    # SET THE first_idx_range THE INDEX OF THE ADDRESS LEVEL ABOVE THE ONE OF THE MAIN ACTION
    last_idx_range = len(splitted_identifier) - 2

    address_level_ref_element = root_address_level_element

    # CLIP THE END PART OF splitted_identifier IN INDEX OF last_idx_range (+1 TO INCLUDE THE LAST INDEX RANGE)
    for idx,current_address_level_idx in enumerate(splitted_identifier[:last_idx_range+1]) : 
        # SKIP THE FIRST ADDRESS LEVEL IDX BECAUSE HIS ADDRESS LEVEL ELEMENT IS THE SAME AS THE INITIAL ONE 
        if idx != 0  : 
            address_level_ref_element = address_level_ref_element.get_sub_address_level_elements()[int(current_address_level_idx)]

        # SELECT THE CURRENT ADDRESS LEVEL ELEMENT IF HIS IDX IN RANGE OF ELEMENT TO BE SELECTED (+1 TO INCLUDE THE LAST INDEX RANGE)
        if idx in range(first_idx_range,last_idx_range+1) : 
            address_level_ref_element.selected = is_select
            address_level_ref_element.save()



def handle_loxbox_areas_long_select_or_deselect_task(splitted_identifier,is_select,additional_action):
    # LOAD THE DJANGO ENV 
    import django
    import os 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    # IMPORTS 
    from WebApi.models import LoxboxCities,LoxboxAreasSelectorProcess
    
    #GRAB THE LOXBOX AREAS SELECTOR PROCESS
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()

    # GRAB THE ROOT ADDRESS LEVEL ELEMENT
    root_address_level_element = LoxboxCities.objects.first()

    # GRAB THE ADDRESS LEVEL ELEMENT
    address_level_element = get_address_level_element(root_address_level_element,splitted_identifier)

    # SET FOR loxbox_areas_selector_process_obj THE INITIAL VALUES OF items_to_process_cnt AND processed_items_cnt
    loxbox_areas_selector_process_obj.progress['processed_items_cnt'] = 0
    # NOTE : I DIDN'T SET THE RIGHT NUMBER TO PROCESS HERE BECAUSE I DIDN'T WANT TO WASTE TIME ON GETTING THE RIGHT NUMBER BY USING THE RECURSIVE SELECT 
    # NOTE : THIS NUMBER IS RIGHT address_level_element.get_items_to_process_cnt() ONLY WHEN THEY ARE ALL DOESN'T EQUAL TO IS_SELECT AND IT'S FALSE WHEN THERE IS SOME OF THEM EQUAL TO IS_SELECT
    loxbox_areas_selector_process_obj.progress['items_to_process_cnt'] = address_level_element.get_items_to_process_cnt(is_select)
    loxbox_areas_selector_process_obj.save()

    # SELECT OR DESELECT RECURSIVELY THE ADDRESS LEVEL ELEMENT 
    select_or_deselect_address_level_element_recursively(address_level_element,is_select,loxbox_areas_selector_process_obj)

    # HANDLE ADDITIONAL ACTION
    if additional_action : 
        # I DIDN'T LOG THE PROGRESS HERE BECAUSE MAX WE WILL 2 ADDITIONAL SELECTS WHICH USUALLY WILL
        # NOT BE LOGGED GIVEN THE LOG INTERVAL 
        handle_additional_action(root_address_level_element,splitted_identifier,additional_action,is_select)

    # LOG THE FINSIH PROGRESS 
    log_loxbox_areas_selector_process_progress(loxbox_areas_selector_process_obj,is_finished=True)
























def init_the_loxbox_selector_process(LoxboxAreasSelectorProcess,items_to_process_cnt): 
    print("INNNNNNNNNNNNNNNNNNNNNNNNNNNNIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIT")
    # SET LoxboxAreasSelectorProcess OBJ TO WORKING AND SET FOR HIM items_to_process_cnt AND processed_items_cnt
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    #loxbox_areas_selector_process_obj.is_working = True 
    loxbox_areas_selector_process_obj.progress['processed_items_cnt'] = 0
    loxbox_areas_selector_process_obj.progress['items_to_process_cnt'] = items_to_process_cnt
    loxbox_areas_selector_process_obj.save()

def select_unselect_all_loxbox_areas(is_select=True):
    # LOAD THE DJANGO ENV
    import django
    import os 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    from WebApi.models import LoxboxAreasSelectorProcess,LoxboxCities

    # INIT THE LOXBOX SELECTOR PROCESS
    processed_items_cnt = 0
    print("START ++++++++++++++++++++++++++++++")
    init_the_loxbox_selector_process(LoxboxAreasSelectorProcess,LoxboxCities.ALL_ELEMENTS_TO_BE_SELECTED_OR_UNSELECTED_COUNT)
    print("END ++++++++++++++++++++++++++++++")
    # SET lx_cities_objEGATION selected_all TO TRUE
    lx_cities_obj = LoxboxCities.objects.first()
    lx_cities_obj.selected = is_select  
    processed_items_cnt += 1 
    lx_cities_obj.save()

    # GRAB THE CITIES OF lx_cities_obj
    cities_qs = lx_cities_obj.city_set.filter(selected=not is_select)
    
    for city_obj in cities_qs : 
        # SET THE CURRENT CITY selected_all TO TRUE AND LOG THE PROGRESS 
        city_obj.selected = is_select 
        city_obj.save()
        processed_items_cnt += 1 
        log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

        # GRAB THE DELEGATIONS OF THE CURRENT CITY
        delgs_qs = city_obj.delegation_set.filter(selected=not is_select)
        for delg_obj in delgs_qs : 
            # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
            delg_obj.selected = is_select
            delg_obj.save()
            processed_items_cnt += 1 
            log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

            # GRAB THE LOCALITIES OF THE CURRENT DELEGATION
            locs_qs = delg_obj.locality_set.filter(selected=not is_select)
            for loc_obj in locs_qs : 
                # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
                loc_obj.selected = is_select 
                loc_obj.save()
                processed_items_cnt += 1 
                print(processed_items_cnt)
                log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

    #LOG THE LAST PROGRESS
    log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt,is_finished=True)



def select_unselect_all_a_city(city_id,is_select=True):
    # LOAD THE DJANGO ENV
    import django
    import os  
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    from WebApi.models import LoxboxAreasSelectorProcess,City

    
    # INIT THE LOXBOX SELECTOR PROCESS
    processed_items_cnt = 0
    city_obj = City.objects.get(id=city_id)
    init_the_loxbox_selector_process(LoxboxAreasSelectorProcess,city_obj.get_items_to_process_cnt())

    # SET city_obj selected_all TO TRUE 
    city_obj.selected = is_select
    city_obj.save()
    processed_items_cnt += 1 

    # GRAB THE DELEGATIONS OF city_obj
    delgs_qs = city_obj.delegation_set.filter(selected=not is_select)

    for delg_obj in delgs_qs : 
        # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
        delg_obj.selected = is_select
        delg_obj.save()
        processed_items_cnt += 1 
        log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

        # GRAB THE LOCALITIES OF THE CURRENT DELEGATION
        locs_qs = delg_obj.locality_set.filter(selected=not is_select)
        for loc_obj in locs_qs : 
            # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
            loc_obj.selected = is_select 
            loc_obj.save()
            processed_items_cnt += 1 
            print(processed_items_cnt)
            log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

    #LOG THE LAST PROGRESS
    log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt,is_finished=True)



def select_unselect_all_a_delegation(delegation_id,is_select=True):
    # LOAD THE DJANGO ENV
    import django
    import os 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    from WebApi.models import LoxboxAreasSelectorProcess,Delegation

    
    # INIT THE LOXBOX SELECTOR PROCESS
    processed_items_cnt = 0
    delegation_obj = Delegation.objects.get(id=delegation_id)
    init_the_loxbox_selector_process(LoxboxAreasSelectorProcess,delegation_obj.get_items_to_process_cnt())

    # SET delegation_obj selected_all TO TRUE 
    delegation_obj.selected = is_select
    delegation_obj.save()
    processed_items_cnt += 1 

    # GRAB THE LOCALITIES OF THE CURRENT delegation_obj
    locs_qs = delegation_obj.locality_set.filter(selected=not is_select)
    for loc_obj in locs_qs : 
        # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
        loc_obj.selected = is_select 
        loc_obj.save()
        processed_items_cnt += 1 
        print(processed_items_cnt)
        log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt,processed_items_log_interval=5)

    #LOG THE LAST PROGRESS
    log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt,is_finished=True)