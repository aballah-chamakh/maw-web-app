# LOAD THE DJANGO ENV

def laad_django_env(): 
    import django
    import os 
    import json 
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
    django.setup()

    test()

def test() : 
    from WebApi.models import LoxboxAreasSelectorProcess,LoxboxCities,City,Delegation,Locality
    print(Locality.objects.count())

laad_django_env()
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