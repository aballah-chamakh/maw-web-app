import requests 

def test() : 
    r = requests.get('https://mawlety.com')
 
try : 
    try : 
        test()
    except Exception as e  : 
        print('inner request ')
except Exception as e :
    print('outer request')

quit()
from MySQLdb import _mysql 
import time 
db=_mysql.connect(host="151.106.100.89",user="anbae24c_pres274",
                  password="NJ@[Sp4l39",database="anbae24c_pres274",port=3306)

db.query(f"""
SELECT Adr.phone_mobile   FROM dal_orders AS Ord
INNER JOIN dal_cart As Ca ON Ord.id_cart = Ca.id_cart AND Ord.current_state IN (3,4,5,14,15,16,13)
INNER JOIN dal_address As Adr ON Ord.id_address_delivery = Adr.id_address 
INNER JOIN dal_cart_product AS Cp ON  Ca.id_cart  = Cp.id_cart
INNER JOIN dal_product AS Pr ON Pr.id_product =  Cp.id_product 
WHERE LENGTH(Adr.phone_mobile) = 8 
""")

 
 # FOR EACH filtered_state_card 
    #   1- GO IT'S LINK 
    #   2- EXTRACT THEIR TRANSACTIONS ID
    #   3- FOR EACH LOXBOX MONITOR ORDER CHECK IF THE ORDER BELONG TO THE CARD STATE USING THE TRANSACTION ID IF SO THEN : 
    #           CHECK IF THE STATE OF THE LOXBOX MONITOR ORDER CHANGED IF SO :
    #               UPDATE THE STATE LOXBOX MONITOR ORDER 
    #               CHECK IF THE UPDATE DB IS TRUE IF SO : 
    #                   CHECK IF THE NEW STATE IN THE DELETE_MONITOR_ORDER_STATES IF SO  :
    #                       DELETE THE MONITOR ORDER FROM THE TABLE
    #                   ELESE : 
    #                       UPDATE THE MONITOR ORDER WITH THE NEW STATE 
    #               UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
    #   4- IF return_monitor_orders_updated == True
    #       return loxbox_monitor_orders
    #     
"""
for filtered_state_card in filtered_state_cards : 
    #1- GO IT'S LINK AND GET THE CORRESPONDING MAWLElY STATE OF THE CURRENT STATE CARD STATE ID TO COMPARE IT WITH STATES OF MONITOR ORDERS
    r = session.get(filtered_state_card['state_card_link'])
    new_mawlety_state = LOXBOX_STATE_ID_TO_MAWLETY_STATE_STR[filtered_state_card['state_card_state_id']]

    #2- EXTRACT THEIR TRANSACTIONS ID
    soup = BeautifulSoup(r.text,"html.parser")
    current_state_card_transactions_id = [el.text for el in soup.select('th > a')]

    #3- FOR EACH LOXBOX MONITOR ORDER CHECK IF THE ORDER BELONG TO THE CARD STATE USING THE TRANSACTION ID IF SO THEN : 
    for idx,loxbox_monitor_order in enumerate(loxbox_monitor_orders) :  
        if str(loxbox_monitor_order['transaction_id']) in current_state_card_transactions_id : 

            if new_mawlety_state != loxbox_monitor_order['state'] :
                
                #CHECK IF THE return_monitor_orders_updated IS FALSE IF SO : 
                if return_monitor_orders_updated == False  : 

                    #CHECK IF THE NEW STATE IN THE DELETE_MONITOR_ORDER_STATES IF SO  : DELETE THE MONITOR ORDER FROM THE TABLE
                    if new_mawlety_state in DELETE_MONITOR_ORDER_STATES : 
                        delete_a_monitor_order_by_id('LOXBOX',loxbox_monitor_order['order_id'])
                    # OTHERWISE UPDATE THE LOXBOX MONITOR ORDER
                    else: 
                        update_a_monitor_order_by_id('LOXBOX',loxbox_monitor_order['order_id'],new_mawlety_state)
                
                #UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
                print("update state in mawlety")
                update_order_state_in_mawlety(loxbox_monitor_order['order_id'],MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID[new_mawlety_state])
                
            # IF return_monitor_orders_updated == True RETURN loxbox_monitor_orders
            if return_monitor_orders_updated == True : 
                if new_mawlety_state != loxbox_monitor_order['state'] :
                    loxbox_monitor_order['state'] = new_mawlety_state
                return loxbox_monitor_orders 
            
            # REMOVE IT FROM loxbox_monitor_orders TO NOT WASTE TIME CHECKING IF HE BELONG TO OTHER CARD STATES 
            loxbox_monitor_orders.pop(idx)

            # BREAK OUT OF THE FUNCTION IF ALL loxbox_monitor_orders ARE POPPED OUT => WE CHECK THE STATE OF ALL THE ORDERS
            if len(loxbox_monitor_orders) == 0 : 
                return 
"""

import requests         
import json 
from bs4 import BeautifulSoup

def get_afex_logged_session(): 
    
    login_data = {
        'station': 'Info@mawlety.com',
        'user_name': 'Info@mawlety.com',
        #'client_id': AFEX_API_CREDENTIALS['client_id'],
        'user_password': '50027541'
    }
    session = requests.Session()
    r = session.post('http://afex.smart-delivery-systems.com/webgesta/index.php/login/process',data=login_data)
    print(r.text)
    print(r.status_code)
    return session

def do_something():
    print(aaaa)

try : 
    #do_something()
    print(aaa)
except Exception:
    print(Exception)


quit()

afex_logged_session  = get_afex_logged_session()

# PREP MANIFESTED ORDERS URL 
afex_manifested_orders_url = "http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/manifest_list?"
afex_manifested_orders_url += f"station=Infor@gmail.com&"
afex_manifested_orders_url += f"client_id=136614&"
afex_manifested_orders_url += "id_prestataire=&"
afex_manifested_orders_url += "is_vendeur_marketplace=&"
afex_manifested_orders_url += f"start_date=2022-01-01&"
afex_manifested_orders_url += f"end_date=2023-01-30&"
afex_manifested_orders_url += "statut=&"
afex_manifested_orders_url += "search_type=date manifest&"
afex_manifested_orders_url += "barcode=&"
afex_manifested_orders_url += "page=1&"
afex_manifested_orders_url += "start=1&"
afex_manifested_orders_url += "limit=60&"

# GRAB AFEX MANIFESTED ORDERS 
r = afex_logged_session.get(afex_manifested_orders_url)
afex_manifested_orders = r.json()['records']

unique_afex_state = []
for afex_manifested_order in afex_manifested_orders: 
    if afex_manifested_order['dernier_statut'] not in unique_afex_state : 
        unique_afex_state.append(afex_manifested_order['dernier_statut'])


print(unique_afex_state)


quit()

url = "http://afex.smart-delivery-systems.com/webgesta/index.php/api/pushOrderDataApi"

for i in range(1) : 
    formatted_afex_order = {
        'client_id': 136614,
        'api_key' : "dKgWBcGVKS7JaTmoL5TP0x1P3Eq9kAij1zDlyztn",
        'nom_pre_destinataire':f"test test {i}",
        'gouvernerat_destinataire':'Ariana',
        'deleg_destinataire':'Ariana Ville',
        'adresse_destinataire' : 'test',
        'tel_destinataire' : 11111111,    
        'marchandise' :  'test',
        #'ref_destinataire' :str(order['id']),
        'nbr_colis' : 1 ,
        'type_envoi_colis' : 'Livraison à domicile',
        'montant_contre_rembst' : 10.0 ,
        'mode_regl' : 'Chèque ou espèces'
    }
    r = requests.post(url,data=formatted_afex_order)


def get_afex_logged_session(): 
    
    login_data = {
        'station': 'Info@mawlety.com',
        'user_name': 'Info@mawlety.com',
        #'client_id': AFEX_API_CREDENTIALS['client_id'],
        'user_password': '50027541'
    }
    session = requests.Session()
    r = session.post('http://afex.smart-delivery-systems.com/webgesta/index.php/login/process',data=login_data)
    print(r.text)
    print(r.status_code)
    return session

afex_logged_session  = get_afex_logged_session()
cookies = afex_logged_session.cookies.get_dict()


r = afex_logged_session.get("http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/expedition_list?station=Info%40mawlety.com&client_id=136614&is_prestataire_marketplace=0&is_vendeur_marketplace=0&page=1&start=0&limit=1000000")
pre_manifest_orders = r.json()['records']
print(r.json()['success'])
print(len(pre_manifest_orders))



manifest_order_keys = ['id', 'num_bord', 'code_a_barre', 'code_a_barre_retour', 'code_depot_dest', 'code_tournee', 'type_envoi_colis', 'gouvernerat_expediteur', 'delegation_expediteur', 'gouvernerat_destinataire', 'deleg_destinataire']
manifest_orders = {'batch':[]}

for pre_manifest_order in pre_manifest_orders :
    manifest_order = {}

    for manifest_order_key in manifest_order_keys : 
        manifest_order[manifest_order_key] = pre_manifest_order[manifest_order_key]
    
    manifest_order['enlevement_status'] = True 
    manifest_orders['batch'].append(manifest_order)

manifest_orders['batch'] = json.dumps(manifest_orders['batch'])
r = afex_logged_session.post("http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/manifest",data=manifest_orders)

print(r.text)
quit()


LOXBOX_BASE_URL = "https://www.loxbox.tn"
LOXBOX_LOGIN_URL = f"{LOXBOX_BASE_URL}/accounts/login/"

LOXBOX_LOGIN_CREDENTIAL  = {
    'username' : 'MawletyProducts',
    'password' : 'N12rIPPK0BZgMG'
}

def get_loxbox_request_status_code(r):
    soup = BeautifulSoup(r.text,"html.parser")
    username = soup.select_one("input[name='username']") 
    password = soup.select_one("input[name='password']") 
    return  401 if username and password else 200 

def login_to_loxbox():
    # GO TO THE LOXBOX LOGIN PAGE AND GET THE csrfmiddlewaretoken OF THE FORM
    s = requests.Session()
    r = s.get(f"{LOXBOX_BASE_URL}/accounts/login/")
    print(s.cookies.get_dict())
    soup = BeautifulSoup(r.text,"html.parser")
    csrfmiddlewaretoken = soup.select_one("input[name='csrfmiddlewaretoken']")['value']
    print(csrfmiddlewaretoken)
    # LOGIN TO LOXBOX USING THE csrfmiddlewaretoken OF THE FORM , THE LOGIN CREDENTIALS AND THE csrftoken FROM THE COOKIE OF THE PREVIOUS REQUEST
    LOXBOX_LOGIN_CREDENTIAL['csrfmiddlewaretoken'] = csrfmiddlewaretoken
    r = s.post(LOXBOX_LOGIN_URL,data=LOXBOX_LOGIN_CREDENTIAL,headers={'referer': LOXBOX_BASE_URL})

    return s,get_loxbox_request_status_code(r)

s,status_code = login_to_loxbox()
cookies =  s.cookies.get_dict()
cookies['sessionid'] += '_xx'
url = "https://www.loxbox.tn/PackagesStatus/0/"

r = s.get(url)
print(f"right cookies : {get_loxbox_request_status_code(r)}")

r = s.get(url,cookies=cookies)
print(f"wrong cookies : {get_loxbox_request_status_code(r)}")
quit()

formatted_afex_order = {
    'client_id': 136614,
    'api_key' : "dKgWBcGVKS7JaTmoL5TP0x1P3Eq9kAij1zDlyztn",
    'nom_pre_destinataire':"test test {i}",
    'gouvernerat_destinataire':'Ariana',
    'deleg_destinataire':'Ariana Ville',
    'adresse_destinataire' : 'test',
    'tel_destinataire' : 11111111,    
    'marchandise' :  'test',
    #'ref_destinataire' :str(order['id']),
    'nbr_colis' : 1 ,
    'type_envoi_colis' : 'Livraison à domicile',
    'montant_contre_rembst' : 10.0 ,
    'mode_regl' : 'Chèque ou espèces'
}


print(r.status_code)
print(f"1 : {r.status_code}")
print(f"1 : {r.text}")
print(f"1 : {r.json()}")

r = requests.post("http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/manifest",data=manifest_orders)
print(r.status_code)
print(f"2 : {r.status_code}")
print(f"2 : {r.text}")
print(f"2 : {r.json()}")


quit()
manifes_base_url = "http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/manifest_list?"
manifes_base_url += "station=Info@mawlety.com&"
manifes_base_url += "client_id=136614&"
manifes_base_url += "id_prestataire=&"
manifes_base_url += "is_vendeur_marketplace=&"
manifes_base_url += "start_date=2023-01-01&"
manifes_base_url += "end_date=2023-01-02&"
manifes_base_url += "statut=&"
manifes_base_url += "search_type=date manifest&"
manifes_base_url += "barcode=&"
manifes_base_url += "page=1&"
manifes_base_url += "start=1&"
manifes_base_url += "limit=60&"

r = afex_logged_session.get(manifes_base_url)
print(len(r.json()['records']))
manifested_orders = r.json()['records'][:10]
for manifested_order in manifested_orders : 
    print(manifested_order['ref_destinataire'])
    
manifested_orders = r.json()['records'][-10:]
for manifested_order in manifested_orders : 
    print(manifested_order['ref_destinataire'])
#print(r.text)
#print(r.json()['records'])
#print(len(r.json()['records']))
quit()

# ?station=Info%40mawlety.com&client_id=136614&id_prestataire=&is_vendeur_marketplace=0
# &start_date=2022-01-01T00%3A00%3A00&end_date=2023-01-27T00%3A00%3A00&statut=&
# search_type=date%20manifest&barcode=&page=1&start=0&limit=60"


#enlevement_status
#true
quit()


login_data = {

'station': 'Info@mawlety.com',
'user_name': 'Info@mawlety.com',
'client_id': 136614,
'user_password': '50027541',

}
r = requests.post('http://afex.smart-delivery-systems.com/webgesta/index.php/login/process',data=login_data)
print(r.json())
quit()

def get_loxbox_header(loxbox_token):
    return {
        'Authorization' : f"Token {loxbox_token}",
        "Content-Type":"application/json"
    }

def format_loxbox_order(loxbox_order) : 
    # customer_detail => firstname,lastname,email
    # address_detail => city,delegation,address1,phone_mobile
    loxbox_order_format = {
    "Content":"any product",
    "detail":"",
    "IsPaid":"0",
    "Price":loxbox_order['total_paid'],
    "Size":"1",
    "Weight":"1" ,
    "DestRelaypoint" : "",
    "ReceiverName" : f"{loxbox_order['customer_detail']['firstname']} {loxbox_order['customer_detail']['lastname']}" ,
    "ReceiverMail" : loxbox_order['customer_detail']['email'],
    "ReceiverNumber" :loxbox_order['address_detail']['phone_mobile'][:8] ,
    "ReceiverAddress" : f"{loxbox_order['address_detail']['address1']},{loxbox_order['address_detail']['city']},{loxbox_order['address_detail']['delegation']},{loxbox_order['address_detail']['locality']}",
    "Comment": f"ORDER ID  : {loxbox_order['id']}",
    "AcceptsCheck" : "1",
    "IsHomeDelivery":"on"    
    }
    return loxbox_order_format

loxbox_header = get_loxbox_header("aaaaaaaaaaaa")
order = {'id': 580, 'id_carrier': '25', 'transaction_id': False, 'address_detail': {'city': 'Sousse', 'delegation': 'Sousse Ville', 'locality': 'Sousse', 'address1': 'Rue poste khzema est', 'phone_mobile': '92872870'}, 'customer_detail': {'firstname': 'Oumayma', 'lastname': 'Ben Miled', 'email': 'benmiledoumaima@yahoo.com'}, 'cart_products': [{'name': 'Soin profond nourrissant cheveux/abîmés', 'quantity': '1'}, {'name': 'Pack cheveux secs et abîmés', 'quantity': '1'}], 'total_paid': '106.500000', 'carrier': 'AFEX', 'selected': True}
formatted_loxbox_order = format_loxbox_order(order)
r = requests.post("https://www.loxbox.tn/api/NewTransaction/",data=json.dumps(formatted_loxbox_order),headers=loxbox_header)
print(type(r.status_code))
print(r.json())


quit()

import requests 
import xml.etree.ElementTree as ET


url = "https://mawlety.com/api/orders/?filter[date_add]=[2023-01-10,2023-01-22]&filter[current_state]=[5]&display=[id,%20total_paid,%20id_carrier,%20transaction_id,%20address_detail,%20customer_detail,%20cart_products,%20current_state]"
token = "UTJCSDlER1pLUUVWSVZDWUQ1UlRYNDcxRTJTTVVRMjQ"

HEADERS = {
    'Authorization' : f'BASIC {token}',
    #'Output-Format' :  'JSON'
}


# GET THE ORDER DATA IN XML STR
orders_base_endpoint = "https://mawlety.com/api/orders/1065"
r = requests.get(orders_base_endpoint,headers=HEADERS)
order_data = r.content.decode()
print(order_data)


# CONVERT THE ORDER DATA INTO XML 
root = ET.fromstring(order_data)
order_tag = root[0]

# UPDATE THE STATE 
current_state = order_tag.find('current_state')
current_state.text = '6'

# REMOVE SOME TAGS 
transaction_id = order_tag.find('transaction_id')
order_tag.remove(transaction_id)

address_detail = order_tag.find('address_detail')
order_tag.remove(address_detail)

customer_detail = order_tag.find('customer_detail')
order_tag.remove(customer_detail)

cart_products = order_tag.find('cart_products')
order_tag.remove(cart_products)

#HEADERS['Authorization'] += "x" 

r = requests.put(orders_base_endpoint,data=ET.tostring(root),headers=HEADERS)

print(r.status_code)
print(r.text)





