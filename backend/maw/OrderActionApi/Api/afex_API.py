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
    
    formatted_afex_order = {
        **AFEX_API_CREDENTIALS, 
        'nom_pre_destinataire':f"{order['customer_detail']['firstname']} {order['customer_detail']['lastname']}",
        'gouvernerat_destinataire':order['address_detail']['city'],
        'deleg_destinataire':order['address_detail']['delegation'],
        'adresse_destinataire' : order['address_detail']['address1'],
        'tel_destinataire' : int(order['address_detail']['phone_mobile']),    
        'marchandise' : marchandise ,
        'ref_destinataire' :str(order['id']),
        'nbr_colis' : 1 ,
        'type_envoi_colis' : 'Livraison à domicile',
        'montant_contre_rembst' : float(order['total_paid']) ,
        'mode_regl' : 'Chèque ou espèces'
    }

    url = "http://afex.smart-delivery-systems.com/webgesta/index.php/api/pushOrderDataApi"

    while True : 
        # SUBMIT THE ORDER TO AFEX SERVER 
        r = requests.post(url,data=formatted_afex_order)


        # CHECK IF THE REQUEST WAS SUCCESSFUL THEN EXIT 'status': 'Unauthorized'
        res = r.json()
        print(res)
        # RETURN UNAUTORIZED STATUS CODE 
        if res.get('status') == 'Unauthorized' :  
            return 401

        if res.get('success') == True  : 
            print(res)
            return 
        
        # OTHERWISE WAIT FOR 2 SECONDS 
        print(f"WE DID ENCOUNTER A ERROR WHILE CREATING THE ORDER WITH THE ID : {order['id']} , WE WILL TRY AGAIN IN 2 SECONDS")
        time.sleep(2)
            

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
            status_code = submit_afex_order(order)

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
        except Exception as e :
            exception_msg = f"THE FOLLOWING ERROR HAPPENED WHILE SUBMITTING THE ORDER WITH THE ID {order['id']} TO AFEX : "
            exception_msg += str(e)+' ,'
            exception_msg += f"PLEASE BACKUP THE STATE OF THE ORDER TO VALIDÉ IN MAWLETY.COM AFTER FIXING YOUR INTERNET CONNECTION" 
            raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)



        add_afex_order_to_monitoring_phase(order)
        
        # INSCREASE THE submitted_orders_len
        orders_submitter_obj.state['progress']['submitted_orders_len']  += 1 
        orders_submitter_obj.save()

        # SLEEP FOR EACH SUBMITTED ORDER TO NOT OVERLOAD THE SERVER 
        time.sleep(2)
        
    # MANIFEST ORDERS 
    try :
        manifest_orders(orders_submitter_obj)
    except Exception as e:
        exception_msg = f"THE FOLLOWING ERROR HAPPENED WHILE TRYING TO MANIFEST THE ORDERS OF AFEX : "
        exception_msg += str(e)+' ,'
        exception_msg += f"PLEASE MANIFEST THE ORDERS OF AFEX AFTER FIXING YOUR INTERNET CONNECTION  : " 
        raise_a_server_request_exception_error(orders_submitter_obj,exception_msg)
         


def afex_state_to_mawlety_state_converter(afex_order_state): 
    afex_state_to_mawlety_state = {

        "en attente d'enlevement" : 'En cours de préparation', 
        'en attente de livraison':'Expédié', 
        'en cours de livraison':'Expédié', 
        'en attente de relivraison':'Expédié',
        'en attente de retour':'Expédié', 
        'en cours de retour':'Expédié',
        'en cours de transfert' : 'Expédié',
        'en attente de transfert' :'Expédié',
        'livre':'Livré',
        'retourne':'Retour',
        'annulé':'Annulé',
        'recupere' : 'Expédié',
        'en attente':'Expédié',
    }
    return afex_state_to_mawlety_state.get(afex_order_state)

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

def update_afex_monitor_orders_state_from_afex(afex_monitor_orders,orders_monitoror_obj):

    # GET THE MANIFEST DATE RANGE OF AFEX MONITOR ORDER
    afex_monitor_orders_manifest_date_range = get_afex_monitor_orders_manifest_date_range(afex_monitor_orders)

    # GRAB THE LOGGED SESSION OF AFEX
    try :
        afex_logged_session,status_code = get_afex_logged_session()
        # HANDLE AN UNAUTHORIZATION ERROR IF IT EXIST 
        if status_code == 401 : 
            raise_a_unathorization_error(orders_monitoror_obj,'INVALID_AFEX_CREDENTIALS')
    except Exception as e:
        exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO LOGIN TO AFEX : '
        exception_msg += str(e)+' ,'
        exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
        raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg)    


    # PREP MANIFESTED ORDERS URL 
    afex_manifested_orders_url = "http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/manifest_list?"
    afex_manifested_orders_url += f"station={AFEX_LOGIN_CREDENTIALS['email']}&"
    afex_manifested_orders_url += f"client_id={AFEX_API_CREDENTIALS['client_id']}&"
    afex_manifested_orders_url += "id_prestataire=&"
    afex_manifested_orders_url += "is_vendeur_marketplace=&"
    afex_manifested_orders_url += f"start_date={afex_monitor_orders_manifest_date_range['start_date']}&"
    afex_manifested_orders_url += f"end_date={afex_monitor_orders_manifest_date_range['end_date']}&"
    afex_manifested_orders_url += "statut=&"
    afex_manifested_orders_url += "search_type=date manifest&"
    afex_manifested_orders_url += "barcode=&"
    afex_manifested_orders_url += "page=1&"
    afex_manifested_orders_url += "start=1&"
    afex_manifested_orders_url += "limit=60&"



    # GRAB AFEX MANIFESTED ORDERS 
    afex_manifested_orders = []
    try : 
        r = afex_logged_session.get(afex_manifested_orders_url)
        afex_manifested_orders = r.json()['records']
    except Exception as e : 
        exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO GRAB ORDERS FROM AFEX : '
        exception_msg += str(e)+' ,'
        exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
        raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg)     

    # CONVERT AFEX MANIFESTED ORDERS INTO A DICT WITH THE FOLLOWING FORMAT  {'order_id':'order_state'}
    afex_manifested_orders_dict = afex_manifested_orders_to_dict(afex_manifested_orders)
    

    # FOR EACH AFEX MONITOR ORDER CHECK IF THE STATE OF THE ORDER WAS UPDATED IF SO DO YOUR THING
    for afex_monitor_order in afex_monitor_orders : 

        # SET THE NEW current_order_id
        orders_monitoror_obj.state['progress']['current_order_id'] = afex_monitor_order.order_id
        orders_monitoror_obj.save()

        # AFEX ORDER STATE FROM DB 
        afex_monitor_order_state = afex_monitor_order.state

        # AFEX ORDER STATE FROM AFEX SITE  
        afex_manifested_order_state =  afex_manifested_orders_dict[str(afex_monitor_order.order_id)] #f"failed_state_{int(random.random()*100)}"

        # CONVERT IT TO MAW STATE
        afex_manifested_order_in_maw_state = afex_state_to_mawlety_state_converter(afex_manifested_order_state.lower()) 

        # HANDLE THE CASE OF THE CONVERTER DIDN'T WORK 
        if not afex_manifested_order_in_maw_state : 

            # SAVE THE CONVESION ERROR
            if not orders_monitoror_obj.state['conv_errors']['AFEX'].get(afex_manifested_order_state.lower()) : 
                orders_monitoror_obj.state['conv_errors']['AFEX'][afex_manifested_order_state.lower()] = 1
            else :
                orders_monitoror_obj.state['conv_errors']['AFEX'][afex_manifested_order_state.lower()] += 1 
            orders_monitoror_obj.save()
            # INCREASE THE MONITOR ORDERS LEN BY ONE 
            orders_monitoror_obj.state['progress']['monitored_orders_len'] += 1 
            orders_monitoror_obj.save()
            # SKIP THIS ORDER AND CONTINUE MONITORING THE OTHER ORDERS 
            continue 



        #CHECK IF THE STATE OF THE CURRENT MONITOR ORDER WAS CHANGED
        if afex_monitor_order_state != afex_manifested_order_in_maw_state  : 
            print("THERE IS A CHANGE")

            #UPDATE THE STATE OF THE ORDER IN MAWLETY.COM
            try : 
                status_code = update_order_state_in_mawlety(afex_monitor_order.order_id,afex_manifested_order_in_maw_state)
                # RAISE AN UNAUTORIZATION ERROR IF IT EXIST 
                if status_code == 401 : 
                    raise_a_unathorization_error(orders_monitoror_obj,'INVALID_MAWLETY_API_KEY')
            except Exception as e : 
                exception_msg = f'THE FOLLOWING ERROR HAPPENED WHILE TRYING TO UPDATE THE STATE OF ORDER WITH THE ID {afex_monitor_order.order_id} IN MAWLETY.COM : '
                exception_msg += str(e)+' ,'
                exception_msg += 'PLEASE FIX YOUR INTERNET CONNECTION'
                raise_a_server_request_exception_error(orders_monitoror_obj,exception_msg) 


            # IF THE NEW STATE IS ONE OF THE DELETE STATE DELETE THE ORDER FROM THE TABLE 
            if afex_manifested_order_in_maw_state in DELETE_MONITOR_ORDER_STATES : 
                delete_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id)
            # OTHERWISE UPDATE THE AFEX MONITOR ORDER
            else:
                update_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id,afex_manifested_order_in_maw_state)




            # ADD THE CHANGED ORDER OBJ TO THE RESULT KEYWORD
            orders_monitoror_obj.state['results'].append({
                'order_id': afex_monitor_order.order_id,
                'carrier' : 'AFEX',
                'old_state' : afex_monitor_order.state,
                'new_state' : afex_manifested_order_in_maw_state
            })
            orders_monitoror_obj.save()

        else : 
            print("NO CHANGE ")
        
        # INCREASE THE MONITOR ORDERS LEN BY ONE 
        orders_monitoror_obj.state['progress']['monitored_orders_len'] += 1 
        orders_monitoror_obj.save()
  
                




    

   