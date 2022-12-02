
def log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt,is_finished=False,processed_items_log_interval=20):
    if is_finished or processed_items_cnt % processed_items_log_interval == 0 : 
        loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
        loxbox_areas_selector_process_obj.progress['processed_items_cnt'] = processed_items_cnt
        if is_finished : 
            loxbox_areas_selector_process_obj.is_working = False 
        loxbox_areas_selector_process_obj.save()

def init_the_loxbox_selector_process(LoxboxAreasSelectorProcess,items_to_process_cnt): 
    print("INNNNNNNNNNNNNNNNNNNNNNNNNNNNIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIT")
    # SET LoxboxAreasSelectorProcess OBJ TO WORKING AND SET FOR HIM items_to_process_cnt AND processed_items_cnt
    loxbox_areas_selector_process_obj = LoxboxAreasSelectorProcess.objects.first()
    loxbox_areas_selector_process_obj.is_working = True 
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
    lx_cities_obj.selected_all = is_select  
    processed_items_cnt += 1 
    lx_cities_obj.save()

    # GRAB THE CITIES OF lx_cities_obj
    cities_qs = lx_cities_obj.city_set.all()
    
    for city_obj in cities_qs : 
        # SET THE CURRENT CITY selected_all TO TRUE AND LOG THE PROGRESS 
        city_obj.selected_all = is_select 
        city_obj.save()
        processed_items_cnt += 1 
        log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

        # GRAB THE DELEGATIONS OF THE CURRENT CITY
        delgs_qs = city_obj.delegation_set.all()
        for delg_obj in delgs_qs : 
            # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
            delg_obj.selected_all = is_select
            delg_obj.save()
            processed_items_cnt += 1 
            log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

            # GRAB THE LOCALITIES OF THE CURRENT DELEGATION
            locs_qs = delg_obj.locality_set.all()
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
    city_obj.selected_all = is_select
    city_obj.save()
    processed_items_cnt += 1 

    # GRAB THE DELEGATIONS OF city_obj
    delgs_qs = city_obj.delegation_set.all()

    for delg_obj in delgs_qs : 
        # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
        delg_obj.selected_all = is_select
        delg_obj.save()
        processed_items_cnt += 1 
        log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt)

        # GRAB THE LOCALITIES OF THE CURRENT DELEGATION
        locs_qs = delg_obj.locality_set.all()
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
    delegation_obj.selected_all = is_select
    delegation_obj.save()
    processed_items_cnt += 1 

    # GRAB THE LOCALITIES OF THE CURRENT delegation_obj
    locs_qs = delegation_obj.locality_set.all()
    for loc_obj in locs_qs : 
        # SET THE CURRENT DELEGATION selected_all TO TRUE AND LOG THE PROGRESS  
        loc_obj.selected = is_select 
        loc_obj.save()
        processed_items_cnt += 1 
        print(processed_items_cnt)
        log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt,processed_items_log_interval=5)

    #LOG THE LAST PROGRESS
    log_loxbox_areas_selector_process_progress(LoxboxAreasSelectorProcess,processed_items_cnt,is_finished=True)