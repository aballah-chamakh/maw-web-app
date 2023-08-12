import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json 
import time
import requests 
from .credentials import AFEX_LOGIN_CREDENTIALS,AFEX_API_CREDENTIALS
from .mawlety_API import update_order_state_in_mawlety 
from .monitoring_API import delete_a_monitor_order_by_id, update_a_monitor_order_by_id,add_afex_order_to_monitoring_phase
from .global_variables import DELETE_MONITOR_ORDER_STATES
from .global_functions import raise_a_unathorization_error,raise_an_exception_error,raise_a_server_request_exception_error


def get_afex_logged_session(): 
    login_data = {
        'station': AFEX_LOGIN_CREDENTIALS['email'],
        'user_name': AFEX_LOGIN_CREDENTIALS['email'],
        'client_id': AFEX_API_CREDENTIALS['client_id'],
        'user_password': AFEX_LOGIN_CREDENTIALS['password'] 
    }
    session = requests.Session()
    r = session.post('http://afex.smart-delivery-systems.com/webgesta/index.php/login/process',data=login_data)
    status_code = r.status_code
    print(r.json())
    if r.json()['success'] == False :
        status_code =  401
    return session,status_code

def get_afex_pre_manifested_orders(afex_logged_session): 
    # PREP AFEX PRE MANIFESTED ORDERS URL 
    afex_pre_manifested_orders_url = "http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/expedition_list?"
    afex_pre_manifested_orders_url += f"station={AFEX_LOGIN_CREDENTIALS['email']}&"
    afex_pre_manifested_orders_url += f"client_id={AFEX_API_CREDENTIALS['client_id']}&"
    afex_pre_manifested_orders_url += "is_prestataire_marketplace=0&"
    afex_pre_manifested_orders_url += "is_vendeur_marketplace=0&"
    afex_pre_manifested_orders_url += "page=1&"
    afex_pre_manifested_orders_url += "start=1&"
    afex_pre_manifested_orders_url += "limit=60&"
   
    r = afex_logged_session.get(afex_pre_manifested_orders_url)

    return r.json()['records']


def manifest_orders(orders_submitter_obj):
    # INIATE THE MANIFEST ORDER KEYS TEMPLATE
    manifest_order_keys = ['id', 'num_bord', 'code_a_barre', 'code_a_barre_retour', 'code_depot_dest', 'code_tournee', 'type_envoi_colis', 'gouvernerat_expediteur', 'delegation_expediteur', 'gouvernerat_destinataire', 'deleg_destinataire']
    
    # GRAB THE LOGGED SESSION OF AFEX 
    afex_logged_session,status_code = get_afex_logged_session()    
    # HANDLE AN UNAUTHORIZATION ERROR IF IT EXIST 
    if status_code == 401 : 
        raise_a_unathorization_error(orders_submitter_obj,'INVALID_AFEX_CREDENTIALS_WHILE_MANIFESTING')

    
    # GRAB AFEX PRE MANIFESTED ORDERS 
    # NOTE THIS REQUEST DOESN'T NEED AUTHORIZATION 
    afex_pre_manifested_orders = get_afex_pre_manifested_orders(afex_logged_session)

    # PREP THE ORDERS TO MANIFEST FROM THE PRE MANIFESTED ORDERS 
    orders_to_manifest = {'batch':[]}
    if afex_pre_manifested_orders :
        for pre_manifest_order in afex_pre_manifested_orders :
            manifest_order = {}

            # POPULATE manifest_order FROM THE PRE MANIFEST ORDER WITH ONLY THE KEYS OF manifest_order_keys
            for manifest_order_key in manifest_order_keys : 
                manifest_order[manifest_order_key] = pre_manifest_order[manifest_order_key]
            
            # ADD enlevement_status KEY VALUE AT THE END BECAUSE IT DOES'T EXIST ON THE PRE MANIFEST ORDER 
            manifest_order['enlevement_status'] = True 

            orders_to_manifest['batch'].append(manifest_order)
        
        orders_to_manifest['batch'] = json.dumps(orders_to_manifest['batch'])
    else : 
        orders_to_manifest['batch'] = ''

    # MANIFEST ORDERS
    # NOTE THIS REQUEST DOESN'T NEED AUTHORIZATION 
    r = afex_logged_session.post("http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/manifest",data=orders_to_manifest)
    print(f"manifest res : {r.text}")
    # CHECK IF THE MANIFEST DIDN'T WORK , IF SO RAISE AN EXCEPTION ERROR
    if not ('success' in r.text and r.json()['success'] == True) : 
        raise_an_exception_error(orders_submitter_obj,'THE_MANIFEST_REQUEST_NOT_WORKING')



def submit_afex_order(order) : 
    marchandise = ""
    cart_product_len = len(order['cart_products'])
    for idx,product in enumerate(order['cart_products']) : 
        marchandise += f"{product['quantity']} x {product['name']}"
        if idx+1 != cart_product_len :
            marchandise += ','
    headers = {
        'Content-Type': "application/text",
        'X-API-Key': AFEX_API_CREDENTIALS['api_key']
    }
    
    formatted_afex_order = {
        'nom':order['address_detail']['firstname'],
        'gouvernorat':order['address_detail']['city'],
        'delegation':order['address_detail']['delegation'],
        'adresse' : order['address_detail']['address1'],
        'telephone1' : order['address_detail']['phone_mobile'], 
        'telephone2' : order['address_detail']['phone'],    
        'marchandise' : marchandise ,
        'reference' :str(order['reference']),
        'paquets' : 1 ,
        'type_envoi' : 'Livraison à domicile',
        'cod' : order['total_paid'] ,
        'mode_reglement' : 'Chèque ou espèces',
        'manifest' : 0 
    }

    url = "https://apis.afex.tn/v1/shipments"

    

    # SUBMIT THE ORDER TO AFEX SERVER 
    r = requests.post(url,data=json.dumps(formatted_afex_order),headers=headers)
    json_res = json.loads(r.text.replace("'",'"')) 
    return json_res , r.status_code 


        
     
            

def submit_afex_orders(orders,orders_submitter_obj):

    # START SUBMITTING ORDERS 
    for order in orders: 
        print(f"WORKING ON SUBMITTING THE ORDER WITH ID : {order['id']}")

        # SET THE CURRENT ORDER ID 
        orders_submitter_obj.state['progress']['current_order_id'] = order['id']
        orders_submitter_obj.save()
        


        try : 
            # UPDATE THE STATE OF THE ORDER IN MAWLETY
            status_code = update_order_state_in_mawlety(order['id'],'En cours de préparation')
            # RAISE AN UNAUTORIZATION ERROR IF IT EXIST 
            if status_code == 401 : 
                raise_a_unathorization_error(orders_submitter_obj,'INVALID_MAWLETY_API_KEY')
        except Exception as e : 
            exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE UPDATING THE STATE OF THE ORDER WITH THE ID {order["id"]} IN MAWLETY.COM : '
            exception_msg += str(e)+' ,'
            exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
            raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)
        

        try :
            
            # SUBMIT THE ORDER TO AFEX  
            r,status_code = submit_afex_order(order)

            # RAISE AN UNAUTORIZATION ERROR IF IT EXIST 
            if status_code == 401 : 
                try : 
                    # UNDO THE UPDATE OF THE STATE OF ORDER IN MAWLETY 
                    status_code = update_order_state_in_mawlety(order['id'],'Validé')

                    # RAISE AN UNAUTORIZATION ERROR ON AFEX AND MAW
                    if status_code == 401 :
                        raise_a_unathorization_error(orders_submitter_obj,f'INVALID_AFEX_AND_MAWLETY_API_KEY_UNDO_ORDER_ID_{order["id"]}')
                    
                    raise_a_unathorization_error(orders_submitter_obj,'INVALID_AFEX_API_KEY')
                except  Exception as e :
                    exception_msg = f"THE FOLLOWING ERROR HAPPENED WHILE TRYING TO BACKUP THE STATE OF THE ORDER WITH THE ID {order['id']} TO VALIDÉ IN MAWLETY.COM AFTER THE SUBMITTING OF THE ORDER TO AFEX WAS UNAUTHORIZED : "
                    exception_msg += str(e)+' ,'
                    exception_msg += f"PLEASE BACKUP THE STATE OF THE ORDER TO VALIDÉ IN MAWLETY.COM THEN UPDATE THE API KEY OF AFEX IN THE SETTING AFTER FIXING YOUR INTERNET CONNECTION" 
                    raise_a_server_request_exception_error(orders_submitter_obj,exception_msg) 
            elif status_code != 200 :
                exception_msg = f"THE STATUS CODE COMMING FROM RESPONSE OF SUBMITTING THE ORDER WIH THE ID : {order['id']} TO AFEX IS : {r.status_code}"
                exception_msg += " ,PLEASE BACKUP THE STATE OF THE ORDER TO VALIDÉ IN MAWLETY.COM AFTER REPORTING THIS ISSUE TO AFEX" 
                raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)

            order['barcode'] = r['barcode']
            add_afex_order_to_monitoring_phase(order)
            
            # INSCREASE THE submitted_orders_len
            orders_submitter_obj.state['progress']['submitted_orders_len']  += 1 
            orders_submitter_obj.save()
    
        except Exception as e :
            exception_msg = f"THE FOLLOWING ERROR HAPPENED WHILE SUBMITTING THE ORDER WITH THE ID {order['id']} TO AFEX : "
            exception_msg += str(e)+' ,'
            exception_msg += f"PLEASE BACKUP THE STATE OF THE ORDER TO VALIDÉ IN MAWLETY.COM AFTER FIXING YOUR INTERNET CONNECTION" 
            raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)




        # SLEEP FOR EACH SUBMITTED ORDER TO NOT OVERLOAD THE SERVER 
        time.sleep(2)
        
     


def afex_state_to_mawlety_state_converter(afex_order_state): 
    afex_state_to_mawlety_state = {
        'pre_manifest' : 'En cours de préparation', 
        'awaiting_removal':'En cours de préparation', 
        'delivered':'Livré',
        'returned':'Retour',
        'canceled':'En cours de retour',
        'pre_shipping_canceling' : 'Annulé'
    }
    return afex_state_to_mawlety_state.get(afex_order_state) or 'Expédié'

def move_date_day(date_str,days):
    return (datetime.datetime.strptime(date_str, "%Y-%m-%d").date() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

def get_afex_monitor_orders_manifest_date_range(orders) : 
    return {'start_date' :  move_date_day(orders.first().manifest_date,-5),'end_date':move_date_day(orders.last().manifest_date,5)}

def afex_manifested_orders_to_dict(afex_manifested_orders): 
    print(type(afex_manifested_orders))
    afex_manifested_orders_dict = {}
    for afex_manifested_order in afex_manifested_orders: 
        afex_manifested_orders_dict[afex_manifested_order['ref_destinataire']] = afex_manifested_order['dernier_statut']   
    return afex_manifested_orders_dict

def get_shipment_by_barcode(barcode,shipments) :
    for idx,shipment in enumerate(shipments) : 
        if int(shipment['barcode']) == barcode : 
            shipments.pop(idx)
            return shipment
    # IF THE SHIPPMENT DOESN'T EXIST GIVE THE STATE OF PRE SHIPPING CANCELING (BECAUSE THE USER HAS DELETE THE ORDER FROM THE CARRIER PLATFORM BEFORE SHIPPING (CANCELING THE ORDER))
    return {'barcode' : str(barcode) , 'state':'pre_shipping_canceling'} 

def update_afex_monitor_orders_state_from_afex(afex_monitor_orders,orders_monitoror_obj):

    # GRAB THE BARCODES OF AFEX MONITOR ORDERS
    afex_monitor_orders_barcodes = [ order.barcode for order in afex_monitor_orders]

    # GRAB THE LIVE STATES OF AFEX MONITOR ORDERS GIVEN THEIR BARCODES
    url = "https://apis.afex.tn/v1/shipments/status"
    headers = {
        'Content-Type': "application/text",
        'X-API-Key': AFEX_API_CREDENTIALS['api_key']
    }
    shipments = []
    try : 

        r = requests.post(url, data=json.dumps({'shipmentIds' : afex_monitor_orders_barcodes}), headers=headers)
       
        if r.status_code == 401 : 
            raise_a_unathorization_error(orders_monitoror_obj,'INVALID_AFEX_API_KEY')

        # HANDLE THE CASE OF HAVING ONE ORDER TO MONITOR AND THIS ORDER DOESN'T EXIST
        elif r.status_code == 404 : 
            shipments = [{'barcode' : afex_monitor_orders_barcodes[0],'state':'pre_shipping_canceling'}]
        else : 
            shipments = json.loads(r.text.replace("'",'"'))['shipments']

    except Exception as e : 
        exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO GRAB THE LIVE STATES OF AFEX ORDERS : '
        exception_msg += str(e)+' ,'
        exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
        raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg) 

    
    # FOR EACH BARCODE OF AN AFEX MONITOR ORDER CHECK IF HIS STATE WAS UPDATED , IF SO UPDATE THE AFEX MONITOR ORDER AND UPDATE THE ORDER IN MAWLETY
    for afex_monitor_order in afex_monitor_orders :

        # SET THE NEW current_order_id
        orders_monitoror_obj.state['progress']['current_order_id'] = afex_monitor_order.order_id
        orders_monitoror_obj.save()

        shipment = get_shipment_by_barcode(afex_monitor_order.barcode,shipments)
        print(f"{afex_monitor_order.barcode} --- {shipment}")
        new_afex_order_state = afex_state_to_mawlety_state_converter(shipment['state'])

        if afex_monitor_order.state != new_afex_order_state :

            #UPDATE THE STATE OF THE ORDER IN MAWLETY.COM
            try : 
                status_code = update_order_state_in_mawlety(afex_monitor_order.order_id,new_afex_order_state)
                # RAISE AN UNAUTORIZATION ERROR IF IT EXIST 
                if status_code == 401 : 
                    raise_a_unathorization_error(orders_monitoror_obj,'INVALID_MAWLETY_API_KEY')
            except Exception as e : 
                exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO UPDATE THE STATE OF ORDER WITH THE ID {afex_monitor_order.order_id} IN MAWLETY.COM : '
                exception_msg += str(e)+' ,'
                exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
                raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg) 

            
            # IF THE NEW STATE IS ONE OF THE DELETE STATE , DELETE THE ORDER FROM THE TABLE 
            if new_afex_order_state in DELETE_MONITOR_ORDER_STATES : 
                delete_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id)
            # OTHERWISE UPDATE THE AFEX MONITOR ORDER
            else:
                update_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id,new_afex_order_state)

            # ADD THE CHANGED ORDER OBJ TO THE RESULT KEYWORD
            orders_monitoror_obj.state['results'].append({
                'order_id': afex_monitor_order.order_id,
                'carrier' : 'AFEX',
                'old_state' : afex_monitor_order.state,
                'new_state' : new_afex_order_state
            })
            orders_monitoror_obj.save()

        # INCREASE THE MONITOR ORDERS LEN BY ONE 
        orders_monitoror_obj.state['progress']['monitored_orders_len'] += 1 
        orders_monitoror_obj.save()

  
                




    

   