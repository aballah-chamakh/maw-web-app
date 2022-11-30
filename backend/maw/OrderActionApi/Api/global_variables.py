from .credentials import MAWLETY_AUTHORIZATION_TOKEN
import json 



HEADERS = {
    'Authorization' : f"BASIC {MAWLETY_AUTHORIZATION_TOKEN}",
}

MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID = {
    'Validé':'3',
    'En cours de préparation':'18',
    'Expédié':'4',
    'Retour':'19',
    'Annulé':'6',
    'Livré':'5'
}


LOXBOX_CARRIER_ID = '108'

THE_BIG_TUNIS = ['Tunis','Ariana','Ben Arous','Mannouba']


LOXBOX_CITIES_DELEGATIONS = {}


#with open('loxbox_cities_dels_locs.json','r',encoding='utf8') as f:
#    LOXBOX_CITIES_DELEGATIONS = json.loads(f.read())

DELETE_MONITOR_ORDER_STATES = ['Retour','Annulé','Livré']

AFEX_MONITOR_ORDER_TABLE_NAME = "afex_monitor_order"
LOXBOX_MONITOR_ORDER_TABLE_NAME = "loxbox_monitor_order"
