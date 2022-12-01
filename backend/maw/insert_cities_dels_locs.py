import django
import os 
import json 
os.environ['DJANGO_SETTINGS_MODULE'] = 'maw.settings'
django.setup()

from WebApi.models import LoxboxCities,City,Delegation,Locality

f = open('og_cities_delgs_locs.json','r',encoding='utf-8')
og_cities_delgs_locs = json.loads(f.read())
f.close()
db_cities_delgs_locs  = {}
for city in City.objects.all() :                     
    db_cities_delgs_locs[city.name] = {}
    for delg in Delegation.objects.all().filter(city=city):
        db_cities_delgs_locs[city.name][delg.name] = []
        for loc in Locality.objects.all().filter(delegation=delg) : 
            db_cities_delgs_locs[city.name][delg.name].append(loc)

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
#print(db_cities_delgs_locs.keys() == og_cities_delgs_locs.keys())
quit()
loxbox_cities_obj = LoxboxCities.objects.first()

for city,delgs in cities_delgs_locs.items():
    city_obj = City.objects.create(loxbox_cities=loxbox_cities_obj,name=city)
    for delg,locs in delgs.items() : 
        delg_obj = Delegation.objects.create(city=city_obj,name=delg)
        for loc in locs  : 
            loc_obj = Locality.objects.create(delegation=delg_obj,name=loc)



