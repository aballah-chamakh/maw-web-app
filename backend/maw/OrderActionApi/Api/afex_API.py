
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
import random
from .credentials import AFEX_LOGIN_CREDENTIALS,AFEX_API_CREDENTIALS
from .custom_wait import input_has_no_empty_value
from .mawlety_API import update_order_state_in_mawlety 
from .monitoring_API import delete_a_monitor_order_by_id, update_a_monitor_order_by_id,add_afex_order_to_monitoring_phase
from .global_variables import AFEX_LOGIN_URL, AFEX_MONITOR_ORDER_TABLE_NAME, DELETE_MONITOR_ORDER_STATES



def load_cities_delgs_locs_postal_codes() : 
    with open("./cities_dels_locs_afex_v1_js.json","r") as f: 
        cities_delg_locs_postal_codes = json.loads(f.read())
        return cities_delg_locs_postal_codes

def load_driver(port=None,headless=False): 
    chrome_driver_path = ChromeDriverManager().install()
    chrome_options = Options()
    chrome_options.headless = False
    
    if port : 
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    
    driver = webdriver.Chrome(chrome_driver_path,options=chrome_options,service_log_path='NUL')
    
    return driver 

# USED IN MULTIPLE SITUATIONS TO WAIT FOR AN ELEMENT TO EXIST GIVEN HIS CSS SELECTOR (OR A CUSTOM WAIT LIKE THE INPUT CASE)
def wait_for_loading(driver,element_selector,relogin=False,quitx=False,input=False): 
    # TRY TO LOCATE AN ELEMENT
    try : 
        element = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.ID, element_selector)) if not input else input_has_no_empty_value((By.CSS_SELECTOR, element_selector)) 
        )
        return element
    except Exception :
       
        # HANDLE THE EXCEPTION
        print("WE WERE WAITING FOR 5 MINUTES FOR THE WINDOW OR THE PAGE TO LOAD OR AN IMPUT TO BE EMPTY")

        # QUIT BECAUSE THIS IS NOT EXPECTED AND THERE A NEW BUG TO HANDLE
        if quitx  : 
            print(f"A NEW BUG TO HANDLE WHEN WE WERE WAITING FOR AN ELEMENT WITH A SELECTOR OF {element_selector} ")
            quit()

        # RELOGIN AFTER WAITING FOR THE INITIAL PAGE TO LOAD  
        if relogin : 
            print("RELOGIN FROM THE WAIT")
            login_to_afex(driver=driver)
        

def login_to_afex(driver=None):
    # GRAB DRIVER FROM THE GLOBALS IF DRIVER IN THE KWARGS IS NONE (IN THE TESTING PHASE) 
    if not driver : 
        driver = globals()['driver']

    # GO TO THE LOGIN PAGE OF AFEX     
    driver.get(AFEX_LOGIN_URL)
   
    # WAIT FOR THE THE LOGIN FORM TO APPEAR WITHIN A MINUTE OTHERWISE RELOGIN 
    try :
        login_form = driver.find_element(By.ID,"login_ship")
        print("THE LOGIN FORM WAS LOADED SUCCESSFUL")
    except:
        print("RELOGIN AFTER 5 SECONDS BECAUSE THE LOGIN FORM WAS NOT LOADED")
        time.sleep(5)
        login_to_afex(driver=driver)
        return 
    
    # FILL THE LOGIN FORM THEN SUBMIT IT 
    print("FILL THE LOGIN FORM THEN SUBMIT IT ")
   
    driver.execute_script("""
        let credentials = arguments[0] ;

        let email_inp = document.querySelector("input[name='user_name']") 
        let password_inp = document.querySelector("input[name='user_password']")
        let login_btn = document.querySelector('.x-toolbar-item .x-btn-inner')

        email_inp.value = credentials.email
        password_inp.value  = credentials.password        

        login_btn.click() """
    ,AFEX_LOGIN_CREDENTIALS)

    # WAIT FOR THE DASHBOAD TO APPEAR OTHERWISE WITHIN A MINUTE RELOGIN
    print("WAIT FOR THE DASHBOAD TO APPEAR OTHERWISE WITHIN A MINUTE RELOGIN")
    wait_for_loading(driver,"envoi-shortcut",relogin=True)


def load_the_order_manager(driver=None):
    if not driver : 
        driver = globals()['driver']

    # LAUNCH THE ORDER SENDER SOFTWARE
    driver.execute_script("document.querySelector('#envoi-shortcut').click()")

    # WAIT FOR ORDER SENDER SOFTWARE TO LOAD WITHIN A MINUTE OTHERWISE QUIT()  TO HANDLE THIS BUG
    wait_for_loading(driver,"add_bord") 

def get_pre_manifest_orders(driver_cookies): 
    request_cookies = {}
    for cookie in driver_cookies : 
        request_cookies[cookie['name']] = cookie['value'] 
    # GRAB ORDERS 
    r = requests.get("http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/expedition_list?station=Info%40mawlety.com&client_id=136614&is_prestataire_marketplace=0&is_vendeur_marketplace=0&page=1&start=0&limit=1000000",cookies=request_cookies)
    return r.json()['records']

def get_afex_logged_session_cookies() : 
    driver = load_driver()
    login_to_afex(driver=driver)
    return driver.get_cookies()

def refresh_and_load_the_order_manager(driver):
    # DISABLE THE BEFORE UNLOAD POPUP
    driver.execute_script("""
        window.onbeforeunload = null;
        window.onunload = null;
    """)

    # REFRESH THE PAGE
    driver.refresh()

    # WAITING FOR THE DASHBOARD TO APPEAR AFTER THE REFRESH
    wait_for_loading(driver,"envoi-shortcut")
    
    # LAUNCH THE ORDER MANAGER SOFTWARE 
    print("LAUNCH THE ORDER MANAGER SOFTWARE")
    driver.execute_script("document.querySelector('#envoi-shortcut').click()")
    
    # WAIT FOR ORDER MANAGER SOFTWARE TO BE LOADED 
    wait_for_loading(driver,"add_bord",quitx=True)


def waiting_for_loading_pre_manifest_orders_recursively(driver,expected_orders_len) : 
    TIMEOUT_SECONDS = 120
    passed_seconds = 0
    # NOTE :  I USED PANELS TO DO NOT MISTAKE IT WITH TABLE OF "Gestion du paiment"
    while not driver.execute_script("""
    let expected_orders_len = arguments[0] 
    let panels = document.querySelectorAll(".x-panel.x-grid.x-fit-item.x-panel-default")
        if(panels){
            let pre_manifest_panel = panels[0]
            if(pre_manifest_panel.querySelector("table.x-grid-table.x-grid-table-resizer")){
                return pre_manifest_panel.querySelectorAll('table.x-grid-table.x-grid-table-resizer tr').length -1 == expected_orders_len
            }
        }
        return false 
    """,expected_orders_len) :
        if passed_seconds == TIMEOUT_SECONDS : 
            refresh_and_load_the_order_manager(driver)
            waiting_for_loading_pre_manifest_orders_recursively(driver,expected_orders_len)
            break 
        print("WAIT 2 MORE SECONDS FOR THE SUBMITTED ORDERS TO APPEAR IN THE TABLE")
        time.sleep(2)
        passed_seconds += 2 

def manifest_orders(expected_orders_len):
    # LOAD THE DRIVER 
    driver = load_driver()

    # LOGIN TO AFEX 
    login_to_afex(driver=driver)

    # LOAD THE ORDER MANAGER 
    load_the_order_manager(driver=driver)

    # WE ARE WAINTING FOR THE PRE MANIFEST ORDERS TO LOAD RECURSIVELY TO HANDLE ANY BLOCK CAN HAPPEN HERE
    waiting_for_loading_pre_manifest_orders_recursively(driver,expected_orders_len)

    # SELECT ALL THE ORDER AND CLICK MANIFEST 
    driver.execute_script("""
        let order_table = document.querySelectorAll('table.x-grid-table.x-grid-table-resizer')[0]
        let event = new MouseEvent('mousedown',{view:window,bubbles: true,
            cancelable: true})
        order_table.querySelectorAll(".x-grid-cell-first").forEach(el=>{el.firstChild.firstChild.dispatchEvent(event)})
        document.querySelector('#imp_bord').nextElementSibling.click()
    """)    

    # WAIT FOR THE MANIFEST CONFIRMATION MESSAGE BOX
    while not driver.execute_script("return document.querySelectorAll('.x-message-box').length") : 
        print("WAIT 2 MORE SECONDS FOR THE MANIFEST CONFIRMATION MESSAGE BOX TO LOAD")
        time.sleep(2)
    
    # CLICK YES TO CONFIRM THE MANIFEST OF THE ORDERS
    driver.execute_script("document.querySelectorAll('.x-message-box button')[1].click()")

    afex_logged_session_cookies = driver.get_cookies()
    
    # WAIT UNTIL THE PRE MANIFEST ORDER LIST TO BE EMPTY TO MAKE SURE THAT THE MANIFEST REQUEST IS SENT TO THE SERVER BEFORE CLOSING THE BROWSER
    while get_pre_manifest_orders(afex_logged_session_cookies) : 
        print("WAIT 2 MORE SECONDS FOR THE PRE MANIFEST ORDER LIST TO BE EMPTY")
        time.sleep(2)

    # WAIT FOR THE PRINT MESSAGE BOX (THE POINT OF WAITING HERE IS TO MAKE SURE THAT MANIFEST REQUEST IS SENT TO THE SERVER BEFORE CLOSING THE BROWSER)
    #while not driver.execute_script("return document.querySelectorAll('.x-message-box').length && document.querySelectorAll('.x-message-box .x-window-body')[0].innerText.includes('Manifest Validé')") : 
    #    print("WAIT 2 MORE SECONDS FOR THE PRINT MESSAGE BOX TO LOAD")
    #    time.sleep(2)
    # CLICK NO TO NOT PRINT
    #driver.execute_script("document.querySelectorAll('.x-message-box button')[2].click()")

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

        # CHECK IF THE REQUEST WAS SUCCESSFUL THEN EXIT 
        res = r.json()
        if res.get('success') == True  : 
            print(res)
            return 
        
        # OTHERWISE WAIT FOR 2 SECONDS 
        print(f"WE DID ENCOUNTER A ERROR WHILE CREATING THE ORDER WITH THE ID : {order['id']} , WE WILL TRY AGAIN IN 2 SECONDS")
        time.sleep(2)

def submit_afex_orders(orders,orders_submitter_obj):

    # GRAB EXISTING PRE MANIFEST ORDERS LEN 
    afex_logged_session_cookies = get_afex_logged_session_cookies()    
    existing_pre_manifest_orders = get_pre_manifest_orders(afex_logged_session_cookies)
    existing_pre_manifest_orders_len = 0 if existing_pre_manifest_orders == None  else len(existing_pre_manifest_orders)
    
    # LOAD CITIERS DELG LOCS
    cities_delgs_locs_postal_codes = load_cities_delgs_locs_postal_codes()

    # START SUBMITTING ORDERS 
    for order in orders: 
        print(f"WORKING ON SUBMITTING THE ORDER WITH ID : {order['id']}")
        
        # SET THE CURRENT ORDER ID 
        orders_submitter_obj.state['progress']['current_order_id'] = order['id']
        orders_submitter_obj.save()

        # ADD FOR EACH ORDER HIS POSTAL CODE
        city =  order['address_detail']['city']
        delegation = order['address_detail']['delegation']
        locality = order['address_detail']['locality']
        order['address_detail']['postal_code'] = cities_delgs_locs_postal_codes[city][delegation][locality]

        # SUBMIT ORDER 
        submit_afex_order(order)
        add_afex_order_to_monitoring_phase(order)
        
        # INSCREASE THE submitted_orders_len
        orders_submitter_obj.state['progress']['submitted_orders_len']  += 1 
        orders_submitter_obj.save()

        # SLEEP FOR EACH SUBMITTED ORDER TO NOT OVERLOAD THE SERVER 
        time.sleep(2)
        
    # MANIFEST ORDERS 
    manifest_orders(existing_pre_manifest_orders_len+len(orders))

def move_date_day(date_str,days):
    return (datetime.datetime.strptime(date_str, "%Y-%m-%d").date() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

def get_orders_date_range(orders) : 
    return {'start_date' :  move_date_day(orders.first().manifest_date,-1),'end_date':move_date_day(orders.last().manifest_date,1)}

def fitlter_orders_manager_by_date_range(driver,orders) : 
    date_range = get_orders_date_range(orders)
    # SET THE DATE RANGE IN THE "SEND" TAB 
    driver.execute_script("""
        let date_range = arguments[0]
        document.querySelector('#date_start input').value = date_range['start_date']
        document.querySelector('#date_end input').value = date_range['end_date']
    """,date_range)

    # CLICK ON THE ORDER MANAGER TAB (IN THIS WAY WILL LOAD THE DATE RANGE NEEDED WITHOUT CLICKING ON THE SEARCH BTN)
    driver.execute_script("document.querySelector('.x-tab-bar .x-box-inner').childNodes[1].click()")

    # WAIT FOR THE ORDER MANAGER PANEL TO LOAD THE ORDERS TABLE
    while driver.execute_script("""
        let order_manager_panel = document.querySelectorAll(".x-panel-body.x-grid-body.x-panel-body-default.x-panel-body-default.x-layout-fit")[1]; 
        return order_manager_panel.classList.contains('x-masked')
        """) :
        print("WAIT 2 MORE SECONDS FOR THE ORDER MANAGER TABLE TO LOAD")
        time.sleep(2)

def afex_state_to_mawlety_state_converter(afex_order_state): 
    afex_state_to_mawlety_state = {
        "en attente d'enlevement" : 'En cours de préparation',
        'en attente de livraison':'Expédié', 
        'en cours de livraison':'Expédié', 
        'en attente de relivraison':'Expédié',
        'en attente de retour':'Expédié', 
        'en cours de retour':'Expédié',
        'en cours de transfert' : 'Expédié',
        'livré':'Livré',
        'retourne':'Retour',
        'annulé':'Annulé',
        'en attente':'Expédié',
    }
    for afex_state in afex_state_to_mawlety_state.keys() : 
        if afex_state in afex_order_state  : 
            return afex_state_to_mawlety_state[afex_state]

    return None 

def update_afex_monitor_orders_state_from_afex(afex_monitor_orders,orders_monitoror_obj):

    print("LOAD THE DRIVER")
    driver = load_driver(headless=True)

    print("LOGIN TO AFEX")
    login_to_afex(driver=driver)

    print("LOAD THE ORDER SENDER")
    load_the_order_manager(driver=driver)

    print("SET THE DATERANGE THEN GO TO THE ORDER MANAGER PANEL")
    fitlter_orders_manager_by_date_range(driver,afex_monitor_orders)

    # EXTRACT ORDERS FROM AFEX IN THE FOLLOWING FORMAT [{'refercence (order_id)':'afex_state'}]
    orders_from_afex = driver.execute_script("""    
        let rows = document.querySelectorAll(".x-panel-body.x-grid-body.x-panel-body-default.x-panel-body-default.x-layout-fit")[1].querySelectorAll('table tr')
        
        let afex_orders = {}
        rows.forEach((row,idx)=>{
            if(idx == 0 || idx == rows.length - 1){
                return 
            }
            let order_reference = row.querySelectorAll('td')[17].innerText
            order_reference  = order_reference.trim()
            if (order_reference){
                let order_state = row.querySelectorAll('td')[24].innerText
               
                afex_orders[order_reference] = order_state
            }
        })
        return afex_orders
    """) 

    driver.quit()


    # FOR EACH AFEX MONITOR ORDER CHECK IF THE STATE OF THE ORDER WAS UPDATED IF SO DO YOUR THING
    for afex_monitor_order in afex_monitor_orders : 

        # SET THE NEW current_order_id
        orders_monitoror_obj.state['progress']['current_order_id'] = afex_monitor_order.order_id
        orders_monitoror_obj.save()

        # AFEX ORDER STATE FROM DB 
        afex_monitor_order_state = afex_monitor_order.state

        # AFEX ORDER STATE FROM AFEX SITE  
        afex_order_state =  orders_from_afex[str(afex_monitor_order.order_id)] #f"failed_state_{int(random.random()*100)}"

        # CONVERT IT TO MAW STATE
        afex_order_in_maw_state = afex_state_to_mawlety_state_converter(afex_order_state.lower()) 

        # HANDLE THE CASE OF THE CONVERTER DIDN'T WORK 
        if not afex_order_in_maw_state : 

            # SAVE THE CONVESION ERROR
            if not orders_monitoror_obj.state['conv_errors']['AFEX'].get(afex_order_state.lower()) : 
                orders_monitoror_obj.state['conv_errors']['AFEX'][afex_order_state.lower()] = 1
            else :
                orders_monitoror_obj.state['conv_errors']['AFEX'][afex_order_state.lower()] += 1 
            orders_monitoror_obj.save()
            # INCREASE THE MONITOR ORDERS LEN BY ONE 
            orders_monitoror_obj.state['progress']['monitored_orders_len'] += 1 
            orders_monitoror_obj.save()
            # SKIP THIS ORDER AND CONTINUE MONITORING THE OTHER ORDERS 
            continue 



        #CHECK IF THE STATE OF THE CURRENT MONITOR ORDER WAS CHANGED
        if afex_monitor_order_state != afex_order_in_maw_state  : 
            print("THERE IS A CHANGE")
            # IF THE NEW STATE IS ONE OF THE DELETE STATE DELETE THE ORDER FROM THE TABLE 
            if afex_order_in_maw_state in DELETE_MONITOR_ORDER_STATES : 
                delete_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id)
            # OTHERWISE UPDATE THE AFEX MONITOR ORDER
            else:
                update_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id,afex_order_in_maw_state)


            # ADD THE CHANGED ORDER TO THE RESULTS

            # CHECK IF results KEYWORD EXIST OTHERWISE ADD IT 
            if orders_monitoror_obj.state.get('results') == None :
                orders_monitoror_obj.state['results'] = []

            # ADD THE CHANGED ORDER OBJ TO THE RESULT KEYWORD
            orders_monitoror_obj.state['results'].append({
                'order_id': afex_monitor_order.order_id,
                'carrier' : 'AFEX',
                'old_state' : afex_monitor_order.state,
                'new_state' : afex_order_in_maw_state
            })
            orders_monitoror_obj.save()

            #UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
            update_order_state_in_mawlety(afex_monitor_order.order_id,afex_order_in_maw_state)
        else : 
            print("NO CHANGE ")
        
        # INCREASE THE MONITOR ORDERS LEN BY ONE 
        orders_monitoror_obj.state['progress']['monitored_orders_len'] += 1 
        orders_monitoror_obj.save()
  
                




    
if __name__ == '__main__': 
    print("LOAD THE DRIVER")
    driver = load_driver(headless=True)
    print("LOGIN TO AFEX")
    login_to_afex()
    orders = []
    for i in range(500,504):
        orders.append(
            {
            'id': i, 
            'id_carrier': '91',
            'transaction_id': False, 
            'address_detail': {'city': 'Tunis', 'delegation': 'La Marsa', 'locality': 'Jardins de Carthage','postal_code':'2078',
            'address1': 'résidence Aziz  Jardins de Carthage', 'phone_mobile': '98482121'}, 
            'customer_detail': {'firstname': 'test', 'lastname': 'test', 'email': 'test@yahoo.fr'}, 
            'cart_products': [{'name': 'TRIO DEFINISSEUR BOUCLES', 'quantity': '1'}],
            'total_paid': '105.300000'
            }
        )

    #submit_orders(driver,orders)
    #orders = get_monitor_orders_by_carrier(AFEX_MONITOR_ORDER_TABLE_NAME)
    #update_afex_monitor_orders_state_from_afex(driver,orders)

"""

    existing_orders_len = 0 
    
    orders = []
    for i in range(10,30):
        orders.append(
            {
            'id': i, 
            'id_carrier': '91',
            'transaction_id': False, 
            'address_detail': {'city': 'Tunis', 'delegation': 'La Marsa', 'locality': 'Jardins de Carthage','postal_code':'2078',
            'address1': 'résidence Aziz  Jardins de Carthage', 'phone_mobile': '98482121'}, 
            'customer_detail': {'firstname': 'test', 'lastname': 'test', 'email': 'test@yahoo.fr'}, 
            'cart_products': [{'name': 'TRIO DEFINISSEUR BOUCLES', 'quantity': '1'}],
            'total_paid': '105.300000'
            }
        )
    ""
        {
        'id': 2504, 
        'id_carrier': '91',
        'transaction_id': False, 
        'address_detail': {'city': 'Tunis', 'delegation': 'La Marsa', 'locality': 'Jardins de Carthage','postal_code':'2078',
        'address1': 'résidence Aziz  Jardins de Carthage', 'phone_mobile': '98482121'}, 
        'customer_detail': {'firstname': 'Zoubeida', 'lastname': ' Ben Romdhane ', 'email': 'zoubeidabrom@yahoo.fr'}, 
        'cart_products': [{'name': 'TRIO DEFINISSEUR BOUCLES', 'quantity': '1'}],
        'total_paid': '105.300000'
        },
        {
        'id': 2505, 
        'id_carrier': '91',
        'transaction_id': False, 
        'address_detail': {'city': 'Tunis', 'delegation': 'La Marsa', 'locality': 'Jardins de Carthage','postal_code':'2078',
        'address1': 'résidence Aziz  Jardins de Carthage', 'phone_mobile': '98482121'}, 
        'customer_detail': {'firstname': 'Zoubeida', 'lastname': ' Ben Romdhane ', 'email': 'zoubeidabrom@yahoo.fr'}, 
        'cart_products': [{'name': 'TRIO DEFINISSEUR BOUCLES', 'quantity': '1'}],
        'total_paid': '105.300000'
        }
    ""
    driver = load_driver() 
    login_to_afex()
    submit_orders(orders)
    #add_afex_orders_to_monitoring_phase(orders)
 


    #print(driver.title)
    #send_order(driver,order,only_fill=True)
    #login_to_afex(driver)
    #send_order(driver,order)

AFEX_STATE_TO_MAWLETY_STATE = {
'en attente d'enlevement' : 'En cours de préparation',
'en attente de livraison':'Expédié', 
'en cours de livraison':'Expédié', 
'en attente de relivraison':'Expédié',
'en attente':'Expédié',
'en attente de retour':'Expédié', 
'en cours de retour':'Expédié',
'Livré':'Livré',
'Retourne':'Retour',
'annulé':'Annulé'
}


    MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID = {
    'Validé':'3',
    'En cours de préparation':'18',
    'Expédié':'4',
    'Retour':'19',
    'Annulé':'6',
    'Livré':'5'
}

let afex_orders = {}

rows.forEach((el,idx)=>{
    if(idx == 0 || idx == rows.length - 1){
        return 
    }
    afex_orders[`${el.querySelectorAll('td')[17]))}`] = `${el.querySelectorAll('td')[24]))}`
})

"""