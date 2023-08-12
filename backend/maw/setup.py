# LOAD THE DJANGO ENV
import time 

def load_django_env(): 
    import django
    import os 
    import json 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    #test()

def test() : 
    from WebApi.models import OrderAction,MONITORING_ORDERS
    from OrderActionApi.Api.mawlety_API import update_order_state_in_mawlety
    orders_monitoror_obj = OrderAction.objects.filter(type=MONITORING_ORDERS).last()
    start = False 
    for order in orders_monitoror_obj.state['results'] : 
        if order['carrier'] == 'AFEX' : 
            if order['order_id'] == 794 : 
                start = True 
            if start == True :
                print(f"order monitoror id : {orders_monitoror_obj.id} || order : {order}")
                update_order_state_in_mawlety(order['order_id'],order['new_state'])
                time.sleep(3)
                    

def test2():
    from MySQLdb import _mysql 
    from WebApi.models import Delegation
    db=_mysql.connect(host="151.106.100.89",user="anbae24c_pres274",
                    password="NJ@[Sp4l39",database="anbae24c_pres274",port=3306)

    db.query(f"""
        SELECT id_address,firstname,lastname,delegation FROM dal_address where delegation != ''
    """)

    r=db.store_result()
    addresses = list(r.fetch_row(maxrows=0,how=1))
    print(len(addresses))
    for idx, address in  enumerate(addresses):
        qs = Delegation.objects.filter(name=address['delegation'].decode())
        if not qs : 
            print(f"address : {address} is not valid")
    db.close()
    




load_django_env()
test2()
"""
EVALUATE THE RESULT OF MONITORING AFEX ORDERS CODE  : 
# GRAB AFEX ORDERS 01 TO 07
orders_from_afex = update_afex_monitor_orders_state_from_afex()

# GRAB ALL MAW ORDERS 30 T0 07
orders_from_mawlety = grab_maw_orders(291,nb_of_days_ago=8)

# FROM ALL THE MAW ORDERS SELECT ONLY AFEX ORDERS 
maw_afex_orders = []
for order in orders_from_mawlety :                :
     if str(order['id']) in order_from_afex.keys() :
             maw_afex_orders.append(order)

# PRINT THE ORDERS WHO DON'T HAVE THE SAME STATE IN MAW AND AFEX
for order in maw_afex_orders : 
    if MAWLETY_STATE_ID_TO_MAWLETY_STR_STATE[order['current_state']] != afex_state_to_mawlety_state_converter(orders_from_afex[str(order['id'])]) : 
        print(order['id'])
        

"""
quit()
# CREATE THE LoxboxAreasSelectorProcess OBJECTS IF IT DOESN'T EXIST 
if LoxboxAreasSelectorProcess.objects.count() == 0  : 
    LoxboxAreasSelectorProcess.objects.create()

# TO DELETE AN OLD INSETION
if LoxboxCities.objects.first() : 
    LoxboxCities.objects.first().delete()

# INSERT CITIES DELGS LOCS 

# LOAD THE og_cities_delgs_locs
f = open('og_cities_delgs_locs.json','r',encoding='UTF-8')
og_cities_delgs_locs = json.loads(f.read())
f.close()



#INIT THE PROGRESS COUNTER
progress_cnt = 0

# GRAB THE loxbox_cities_obj OR CREATE A ONE 
loxbox_cities_obj = LoxboxCities.objects.first() or LoxboxCities.objects.create()
progress_cnt += 1

# TO DELETE AN OLD INSETION
# LoxboxCities.objects.first().delete()

for city,delgs in og_cities_delgs_locs.items():
    city_obj = City.objects.create(loxbox_cities=loxbox_cities_obj,name=city)
    progress_cnt += 1 
    for delg,locs in delgs.items() : 
        delg_obj = Delegation.objects.create(city=city_obj,name=delg)
        progress_cnt += 1 
        for loc in locs  : 
            loc_obj = Locality.objects.create(delegation=delg_obj,name=loc)
            progress_cnt += 1 
            print(f"{progress_cnt} / {LoxboxCities.ALL_ELEMENTS_TO_BE_SELECTED_OR_UNSELECTED_COUNT} WERE INSERTED")



# CHECK IF THE DATA WERE INSERTED CORRECTLY

# PREPARE THE db_cities_delgs_locs
db_cities_delgs_locs  = {}
for city in City.objects.all() :                     
    db_cities_delgs_locs[city.name] = {}
    for delg in Delegation.objects.all().filter(city=city):
        db_cities_delgs_locs[city.name][delg.name] = []
        for loc in Locality.objects.all().filter(delegation=delg) : 
            db_cities_delgs_locs[city.name][delg.name].append(loc.name)

# CHECK IF THE DATA WERE INSERTED CORRECTLY + SHOW WHERE THE PROBLEM EXIST 
for city,delgs in og_cities_delgs_locs.items():
    for delg,locs in delgs.items() : 
        if delg not in db_cities_delgs_locs[city].keys(): 
            print(f"PROBLEM AT CITY : {city} DELEGATION : {delg} DOES NOT EXIST")
            print(f"DB DELGS : {db_cities_delgs_locs[city].keys()}")
            quit() 
        for loc in locs : 
            if loc not in db_cities_delgs_locs[city][delg] : 
                print(f"PROBLEM AT CITY : {city} DELEGATION : {delg} LOCALITY {loc} DOES NOT EXIST")
                print(f"DB LOCS : {db_cities_delgs_locs[city][delg]}")
                quit()

# SHOW THE RESULT
if db_cities_delgs_locs == og_cities_delgs_locs : 
    print("THE DATA WAS INSERTED CORRECLTY")
else: 
    print("THE DATA WASN'T INSERTED CORRECLTY")