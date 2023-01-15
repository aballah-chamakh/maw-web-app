from .credentials import MAWLETY_AUTHORIZATION_TOKEN


AFEX_LOGIN_URL = "http://afex.smart-delivery-systems.com/webgesta/index.php/login"

HEADERS = {
    'Authorization' : f"BASIC {MAWLETY_AUTHORIZATION_TOKEN}",
}


MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID = {
    'Validé':'3',
    'En cours de préparation':'16',
    'Expédié':'4',
    'Retour':'17',
    'Annulé':'6',
    'Livré':'5'
}

MAWLETY_STATE_ID_TO_MAWLETY_STR_STATE= {
    '3':'Validé',
    '16':'En cours de préparation',
    '4':'Expédié',
    '17':'Retour',
    '6':'Annulé',
    '5':'Livré'
}


LOXBOX_CARRIER_ID = '24'

THE_BIG_TUNIS = ['Tunis','Ariana','Ben Arous','Mannouba']


LOXBOX_CITIES_DELEGATIONS = {}


#with open('loxbox_cities_dels_locs.json','r',encoding='utf8') as f:
#    LOXBOX_CITIES_DELEGATIONS = json.loads(f.read())

DELETE_MONITOR_ORDER_STATES = ['Retour','Annulé','Livré']

AFEX_MONITOR_ORDER_TABLE_NAME = "afex_monitor_order"
LOXBOX_MONITOR_ORDER_TABLE_NAME = "loxbox_monitor_order"

