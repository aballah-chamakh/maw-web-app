import time
from bs4 import BeautifulSoup
import requests  
import json 
import random
from .credentials import LOXBOX_LOGIN_CREDENTIAL
from .global_variables import DELETE_MONITOR_ORDER_STATES, HEADERS ,LOXBOX_MONITOR_ORDER_TABLE_NAME
from .mawlety_API import update_order_state_in_mawlety,MAWLATY_API_BASE_URL



LOXBOX_BASE_URL = "https://www.loxbox.tn"
LOXBOX_LOGIN_URL = f"{LOXBOX_BASE_URL}/accounts/login/"

LOXBOX_STATE_ID_TO_MAWLETY_STATE_STR = {
    '0':'En cours de préparation',
    '1':'Expédié',
    '22' : 'Expédié',
    '33' : 'Expédié',
    '44' : 'Expédié',
    '6' : 'Expédié',
    '7' : 'Livré',
    '8' : 'Expédié',
    '9' : 'Expédié',
    '10' : 'Retour',
    '11' : 'Annulé',
}

LOXBOX_STATE_STR_TO_MAWLETY_STATE_STR = {
    'colis préparés':'En cours de préparation',
    'déposé au point relais':'Expédié',
    'collected by transportor' : 'Expédié',
    'colis au centre de tris' : 'Expédié',
    "en cours d'acheminement" : 'Expédié',
    'colis déposé au point relais' : 'Expédié',
    'colis livrés' : 'Livré',
    'colis mis en retour ' : 'Expédié',
    'in return' : 'Expédié',
    'colis retournés' : 'Retour',
    'colis annulés' : 'Annulé',
}
TAB = "    "

def login_to_loxbox():
    # GO TO THE LOXBOX LOGIN PAGE AND GET THE csrfmiddlewaretoken OF THE FORM

    s = requests.Session()
    r = s.get(f"{LOXBOX_BASE_URL}/accounts/login/")
    soup = BeautifulSoup(r.text,"html.parser")
    csrfmiddlewaretoken = soup.select_one("input[name='csrfmiddlewaretoken']")['value']

    # LOGIN TO LOXBOX USING THE csrfmiddlewaretoken OF THE FORM , THE LOGIN CREDENTIALS AND THE csrftoken FROM THE COOKIE OF THE PREVIOUS REQUEST
    LOXBOX_LOGIN_CREDENTIAL['csrfmiddlewaretoken'] = csrfmiddlewaretoken
    r = s.post(LOXBOX_LOGIN_URL,data=LOXBOX_LOGIN_CREDENTIAL,headers={'referer': LOXBOX_BASE_URL})
    return s

def get_filtered_state_cards(session):
    # SET THE PREFERED LANGUAGE AS FRENCH TO BING THE STATE CARDS NAME IN FRENCH 
    lang_headers = {
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6'
    }
    
    # GOT TO THE DASHBOARD PAGE
    r = session.get(f"{LOXBOX_BASE_URL}/",headers=lang_headers)

    # EXTRACT STATE CARD WITH ORDER NB > 0 
    soup = BeautifulSoup(r.text,"html.parser")
    state_cards = soup.select(".Add_box")
    filtered_state_cards = []

    for state_card in state_cards : 

        current_card_orders_nb = int(state_card.select_one('.card-body').text.split(':')[1].replace('(','').replace(')',''))
        if current_card_orders_nb > 0 : 
            # PREPARE STATE CARD LINK AND ID 
            state_card_link = f"{LOXBOX_BASE_URL}{state_card.select_one('#layoutSidenav_content a')['href']}"
            #state_card_state_id = state_card.select_one('#layoutSidenav_content a')['href'].split('/')[2]
            state_card_name = state_card.select_one('.card-body').text.split(':')[0].strip().lower()


            # EXTRACT TRANSACTIONS ID OF THE STATE CARD 
            r = session.get(state_card_link)
            soup = BeautifulSoup(r.text,"html.parser")
            state_card_transactions_id = [el.text for el in soup.select('th > a')]
            
            # ADD IT TO THE FILTERED STATE CARDS
            filtered_state_cards.append({'transactions_id':state_card_transactions_id,'name' : f"failed_state_{int(random.random()*100)}" }) #state_card_name.lower()})
    
    return filtered_state_cards

def update_monitor_orders_state_from_loxbox(loxbox_monitor_orders,orders_monitoror_obj,update_a_monitor_order_by_id,delete_a_monitor_order_by_id):
    # LOGIN TO LOXBOX
    session = login_to_loxbox()

    # GET THE FILTERED STATE CARDS WITH THEIR DATA (FILTER IN THE ONES WHO HAVE ORDERS IN THEM)
    filtered_state_cards = get_filtered_state_cards(session)

    # CHECK IF results KEYWORD EXIST OTHERWISE ADD IT 
    if orders_monitoror_obj.state.get('results') == None :
        orders_monitoror_obj.state['results'] = []
    
    # FOREACH LOXBOX MONITOR ORDER
    for loxbox_monitor_order in loxbox_monitor_orders : 

        orders_monitoror_obj.state['progress']['current_order_id'] = loxbox_monitor_order.order_id
        orders_monitoror_obj.save()

        # SEARCH IN WHICH STATE CARD THE CURRENT MONITOR ORDER EXIST
        for filtered_state_card in filtered_state_cards : 
            # CHECK IF THE CURRENT MONITOR ORDER EXIST IN THIS STATE CARD
            if loxbox_monitor_order.transaction_id in filtered_state_card['transactions_id'] : 
                
                filtered_state_card_state = LOXBOX_STATE_STR_TO_MAWLETY_STATE_STR.get(filtered_state_card['name'])
                
                # HANDLE THE CASE OF THE FILTERED STATE CARD DON'T CONVERT TO ANY MAWLETY STATE
                if not filtered_state_card_state  : 
                    if not orders_monitoror_obj.state['conv_errors']['LOXBOX'].get(filtered_state_card['name']) : 
                        orders_monitoror_obj.state['conv_errors']['LOXBOX'][filtered_state_card['name']] = 1
                    else : 
                        orders_monitoror_obj.state['conv_errors']['LOXBOX'][filtered_state_card['name']] += 1
                    orders_monitoror_obj.save()
                    break 

                # CHECK IF THE CURRENT MONITOR ORDER WERE CHANGED
                if loxbox_monitor_order.state != filtered_state_card_state : 
        
                    #CHECK IF THE NEW STATE IN THE DELETE_MONITOR_ORDER_STATES IF SO  : DELETE THE MONITOR ORDER FROM THE TABLE
                    if filtered_state_card_state in DELETE_MONITOR_ORDER_STATES : 
                        delete_a_monitor_order_by_id('LOXBOX',loxbox_monitor_order.order_id)

                    # OTHERWISE UPDATE THE LOXBOX MONITOR ORDER
                    else: 
                        update_a_monitor_order_by_id('LOXBOX',loxbox_monitor_order.order_id,filtered_state_card_state)
                               
                    # ADD THE CHANGED ORDER OBJ TO THE RESULT KEYWORD
                    orders_monitoror_obj.state['results'].append({
                        'order_id': loxbox_monitor_order.order_id,
                        'carrier' : 'LOXBOX',
                        'old_state' : loxbox_monitor_order.state,
                        'new_state' : filtered_state_card_state
                    })

                    orders_monitoror_obj.save()

                    #UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
                    print("update state in mawlety")
                    print(f"UPDATE TRANSACTION ID : {loxbox_monitor_order.transaction_id}")
                    update_order_state_in_mawlety(loxbox_monitor_order.order_id,filtered_state_card_state)
                    
                # BREAK ONCE WE FIND IN WHICH STATE CARD THE CURRENT LOXBOX MONITOR ORDER EXITS AND WE DID PROCESS 
                break 

        # UPDATE THE PROGRESS OF MONITORING ORDERS 
        orders_monitoror_obj.state['progress']['monitored_orders_len'] += 1 
        orders_monitoror_obj.save()
         


        
def get_loxbox_header(loxbox_token):
    return {
        'Authorization' : f"Token {loxbox_token}",
        "Content-Type":"application/json"
    }

def get_loxbox_token():
    # SET THE JSON FORMAT AND THE CONFIGUTATION BASE ENDPOINT
    HEADERS['Output-Format'] = "JSON"
    config_base_endpoint = f"/configurations/"

    # GET LOXBOX TOKEN ID
    config_list_filter_endpoint = f"{config_base_endpoint}?filter[name]=loxbox&display=[value]"
    r = requests.get(f"{MAWLATY_API_BASE_URL+config_list_filter_endpoint}",headers=HEADERS)
    loxbox_token = r.json()["configurations"][0]["value"]

    # CLEAN THE JSON FORMAT FOR THE OTHER REQUEST AND RETURN THE LOXBOX TOKEN
    del HEADERS['Output-Format']
    return loxbox_token

def get_order_content(cart_products) : 
    content = "" 
    for idx,cart_product in enumerate(cart_products): 
        content += f"{cart_product['quantity']} x {cart_product['name']}"
        if idx != len(cart_products) - 1 : 
            content+=" , "
    return content

def format_loxbox_order(loxbox_order) : 
    # customer_detail => firstname,lastname,email
    # address_detail => city,delegation,address1,phone_mobile
    loxbox_order_format = {
    "Content":get_order_content(loxbox_order['cart_products']),
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


def insert_a_loxbox_order(loxbox_order,loxbox_header):
    formatted_loxbox_order = format_loxbox_order(loxbox_order)

    while True : 
        r = requests.post("https://www.loxbox.tn/api/NewTransaction/",data=json.dumps(formatted_loxbox_order),headers=loxbox_header)
        
        if r.status_code == 200 : 
            return r.json()['Transaction_instance']
    
        print(f"WE DID ENCOUNTER AN ERROR WHILE CREATING THE ORDER WITH THE ID : {loxbox_order['id']} , WE WILL TRY AGAIN IN 2 SECONDS")
        time.sleep(2)


def submit_loxbox_orders(loxbox_orders,orders_submitter_obj,add_a_loxbox_order_to_monitoring_phase):
    loxbox_token = get_loxbox_token()
    loxbox_header = get_loxbox_header(loxbox_token)
    already_created = True 
    real_cnt = 0
    for loxbox_order in loxbox_orders : 
        
        # SET THE current_order_id TO THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress']['current_order_id'] = loxbox_order['id']
        orders_submitter_obj.save() 

        # IF WE HAVE THE TRANSACTION ID IT MEAN THAT THE TRANSACTION WAS CREATED BY THE LOXBOX MODULE OTHERWISE WE SHOULD CREATE IT BY OURSELF
        if not loxbox_order['transaction_id'] :
            already_created = False
            transaction_id = insert_a_loxbox_order(loxbox_order,loxbox_header)
            real_cnt += 1 
            time.sleep(3)
            loxbox_order['transaction_id'] = transaction_id

        add_a_loxbox_order_to_monitoring_phase(loxbox_order,already_created)
        # INSCREASE submitted_orders_len TO THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress']['submitted_orders_len']  += 1 
        orders_submitter_obj.state['real_cnt']=  real_cnt
        orders_submitter_obj.save()


        

