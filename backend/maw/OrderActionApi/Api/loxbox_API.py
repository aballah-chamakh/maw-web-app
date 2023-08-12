import time
from bs4 import BeautifulSoup
import requests  
import json 
import random
from .credentials import LOXBOX_LOGIN_CREDENTIAL,LOXBOX_API_CREDENTIAL
from .global_variables import DELETE_MONITOR_ORDER_STATES
from .global_functions import raise_a_unathorization_error,raise_a_server_request_exception_error
from .mawlety_API import update_order_state_in_mawlety



LOXBOX_BASE_URL = "https://www.loxbox.tn"
LOXBOX_LOGIN_URL = f"{LOXBOX_BASE_URL}/accounts/login/"

# UNUSED 
LOXBOX_STATE_ID_TO_MAWLETY_STATE_STR = {
    '0':'En cours de préparation',
    '1':'Expédié',
    '22' : 'Expédié',
    '33' : 'Expédié',
    '44' : 'Expédié',
    '6' : 'Expédié',
    '7' : 'Livré',
    '8' : 'Expédié',
    '9' : 'En cours de retour',
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
    'colis mis en retour' : 'Expédié',
    'in return' : 'En cours de retour',
    'colis retournés' : 'Retour',
    'colis annulés' : 'Annulé',
}

TAB = "    "

def get_loxbox_request_status_code(r):
    soup = BeautifulSoup(r.text,"html.parser")
    username = soup.select_one("input[name='username']") 
    password = soup.select_one("input[name='password']") 
    return  401 if username and password else 200 

def login_to_loxbox():
    # GO TO THE LOXBOX LOGIN PAGE AND GET THE csrfmiddlewaretoken OF THE FORM
    s = requests.Session()
    r = s.get(f"{LOXBOX_BASE_URL}/accounts/login/")
    soup = BeautifulSoup(r.text,"html.parser")
    csrfmiddlewaretoken = soup.select_one("input[name='csrfmiddlewaretoken']")['value']

    # LOGIN TO LOXBOX USING THE csrfmiddlewaretoken OF THE FORM , THE LOGIN CREDENTIALS AND THE csrftoken FROM THE COOKIE OF THE PREVIOUS REQUEST
    LOXBOX_LOGIN_CREDENTIAL['csrfmiddlewaretoken'] = csrfmiddlewaretoken
    r = s.post(LOXBOX_LOGIN_URL,data=LOXBOX_LOGIN_CREDENTIAL,headers={'referer': LOXBOX_BASE_URL})
    return s,get_loxbox_request_status_code(r)

def get_filtered_state_cards(session,orders_monitoror_obj):
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
            # HANDLE UNAUTHORIZATION ERROR IF IT EXIST 
            if get_loxbox_request_status_code(r) == 401 : 
                # UPDATE THE SESSION COOKIES WITH A RELOGIN
                session,status_code = login_to_loxbox()
                # HANDLE UNAUTHORIZATION ERROR IF IT EXIST 
                if status_code == 401 : 
                    raise_a_unathorization_error(orders_monitoror_obj,'INVALID_LOXBOX_CREDENTIALS')
                r = session.get(state_card_link)

            soup = BeautifulSoup(r.text,"html.parser")
            state_card_transactions_id = [el.text for el in soup.select('th > a')]
            
            # ADD IT TO THE FILTERED STATE CARDS
            filtered_state_cards.append({'transactions_id':state_card_transactions_id,'name' : state_card_name.lower()}) #f"failed_state_{int(random.random()*100)}" }) #
    
    return filtered_state_cards

def update_monitor_orders_state_from_loxbox(loxbox_monitor_orders,orders_monitoror_obj,update_a_monitor_order_by_id,delete_a_monitor_order_by_id):
    # LOGIN TO LOXBOX
    try :
        session,status_code = login_to_loxbox()
        if status_code == 401 : 
            raise_a_unathorization_error(orders_monitoror_obj,'INVALID_LOXBOX_CREDENTIALS')
    except Exception as e:
        exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO LOGIN TO LOXBOX : '
        exception_msg += str(e)+' ,'
        exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
        raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg)         



    # GET THE FILTERED STATE CARDS WITH THEIR DATA (FILTER IN THE ONES WHO HAVE ORDERS IN THEM)
    filtered_state_cards = []
    try : 
        filtered_state_cards = get_filtered_state_cards(session,orders_monitoror_obj)
    except Exception as e : 
        exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO GRAB ORDERS FROM LOXBOX.TN : '
        exception_msg += str(e)+' ,'
        exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
        raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg)       

    
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
                    
                    #UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
                    print("update state in mawlety")
                    print(f"UPDATE TRANSACTION ID : {loxbox_monitor_order.transaction_id}")
                    try : 
                        status_code = update_order_state_in_mawlety(loxbox_monitor_order.order_id,filtered_state_card_state)
                        # RAISE AN UNAUTORIZATION ERROR IF IT EXIST 
                        if status_code == 401 : 
                            raise_a_unathorization_error(orders_monitoror_obj,'INVALID_MAWLETY_API_KEY')
                    except Exception as e :
                        exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO UPDATE THE STATE OF THE ORDER WITH THE ID {loxbox_monitor_order.order_id} IN MAWLETY.COM: '
                        exception_msg += str(e)+' ,'
                        exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
                        raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg)       

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
    comment =  f"Téléphone2 : {loxbox_order['address_detail']['phone']} --- " if loxbox_order['address_detail']['phone_mobile'] else ""
    loxbox_order_format = {
    "Content":get_order_content(loxbox_order['cart_products']),
    "detail":"",
    "IsPaid":"0",
    "Price":loxbox_order['total_paid'],
    "Size":"1",
    "Weight":"1" ,
    "DestRelaypoint" : "",
    "ReceiverName" : loxbox_order['address_detail']['firstname'] ,
    "ReceiverMail" : 'guest@mawlety.com',
    "ReceiverNumber" :f"{loxbox_order['address_detail']['phone_mobile']}" , # {loxbox_order['address_detail']['phone']}
    "ReceiverAddress" : f"{loxbox_order['address_detail']['address1']},{loxbox_order['address_detail']['locality']},{loxbox_order['address_detail']['delegation']},{loxbox_order['address_detail']['city']}",
    "Comment": f"{comment}Ref : {loxbox_order['reference']}",
    "AcceptsCheck" : "1",
    "IsHomeDelivery":"on"    
    }
    return loxbox_order_format





def insert_a_loxbox_order(loxbox_order,loxbox_header,orders_submitter_obj):
    formatted_loxbox_order = format_loxbox_order(loxbox_order)
    print(formatted_loxbox_order)
    while True : 
        r = requests.post("https://www.loxbox.tn/api/NewTransaction/",data=json.dumps(formatted_loxbox_order),headers=loxbox_header)
        if r.status_code == 200 : 
            return r.json()['Transaction_instance'],r.status_code
        elif r.status_code == 401 :
            return '',r.status_code
        print(f"WE DID ENCOUNTER AN ERROR WHILE CREATING THE ORDER WITH THE ID : {loxbox_order['id']} , WE WILL TRY AGAIN IN 2 SECONDS")
        time.sleep(2)


def submit_loxbox_orders(loxbox_orders,orders_submitter_obj,add_a_loxbox_order_to_monitoring_phase):
    loxbox_token = LOXBOX_API_CREDENTIAL['api_key']
    loxbox_header = get_loxbox_header(loxbox_token)
    submitted_orders_cnt = 0
    for loxbox_order in loxbox_orders : 
        
        # SET THE current_order_id TO THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress']['current_order_id'] = loxbox_order['id']
        orders_submitter_obj.save() 
        
        try : 
            # UPDATE THE STATE OF THE ORDER IN MAWLETY TO "En cours de préparation"
            status_code = update_order_state_in_mawlety(loxbox_order['id'],'En cours de préparation') 
            # RAISE AN UNAUTORIZATION ERROR IF IT EXIST 
            if status_code == 401 : 
                raise_a_unathorization_error(orders_submitter_obj,'INVALID_MAWLETY_API_KEY')
        except Exception as e  : 
            exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE UPDATING THE STATE OF THE ORDER WITH THE ID {loxbox_order["id"]} IN MAWLETY.COM : '
            exception_msg += str(e)+' ,'
            exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
            raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)
        

        # IF WE HAVE THE TRANSACTION ID IT MEAN THAT THE TRANSACTION WAS CREATED BY THE LOXBOX MODULE OTHERWISE WE SHOULD CREATE IT BY OURSELF
        if not loxbox_order['transaction_id'] :
            try : 
                transaction_id,status_code = insert_a_loxbox_order(loxbox_order,loxbox_header,orders_submitter_obj)
                
                # RAISE AN UNAUTORIZATION ERROR IF IT EXIST 
                if status_code == 401 : 
                    try : 
                        # UNDO THE UPDATE OF THE STATE OF ORDER IN MAWLETY 
                        status_code = update_order_state_in_mawlety(loxbox_order['id'],'Validé')
                        # RAISE AN UNAUTORIZATION ERROR ON LX AND MAW
                        if status_code == 401 :
                            raise_a_unathorization_error(orders_submitter_obj,f'INVALID_LOXBOX_AND_MAWLETY_API_KEY_UNDO_ORDER_ID_{loxbox_order["id"]}')
                        
                        raise_a_unathorization_error(orders_submitter_obj,'INVALID_LOXBOX_API_KEY')
                    except Exception as e :
                        exception_msg = f"THE FOLLOWING ERROR HAPPENED WHILE TRYING TO BACKUP THE STATE OF THE ORDER WITH THE ID {loxbox_order['id']} TO VALIDÉ IN MAWLETY.COM AFTER THE SUBMITTING OF THE ORDER TO LOXBOX WAS UNAUTHORIZED : "
                        exception_msg += str(e)+' '
                        exception_msg += f"PLEASE BACKUP THE STATE OF THE ORDER TO VALIDÉ IN MAWLETY.COM THEN UPDATE THE API KEY OF LOXBOX IN THE SETTING AFTER FIXING YOUR INTERNET CONNECTION" 
                        raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)

            except Exception as e :
                exception_msg = f"THE FOLLOWING ERROR HAPPENED WHILE SUBMITTING THE ORDER WITH THE ID {loxbox_order['id']} TO LOXBOX : "
                exception_msg += str(e)+' ,'
                exception_msg += f"PLEASE BACKUP THE STATE OF THE ORDER TO VALIDÉ IN MAWLETY.COM AFTER FIXING YOUR INTERNET CONNECTION" 
                raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)

            # SET THE TRANSACTION ID OF THE LX ORDER 
            loxbox_order['transaction_id'] = transaction_id
            
            # UPDATE THE NUMBER OF ORDERS SUBMITTED WITH THE API (THIS NUMBER DON'T INCLUDE THE ORDERS WHO WERE ALREADY CREATED IN LOXBOX BY THE PS MODDULE) 
            submitted_orders_cnt += 1 
            time.sleep(3)
        


        add_a_loxbox_order_to_monitoring_phase(loxbox_order)

        # INSCREASE submitted_orders_len TO THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress']['submitted_orders_len']  += 1 
        orders_submitter_obj.state['real_cnt']=  submitted_orders_cnt
        orders_submitter_obj.save()


        

