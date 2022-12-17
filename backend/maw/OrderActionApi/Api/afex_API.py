
import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json 
import time
from .credentials import AFEX_LOGIN_CREDENTIALS
from .custom_wait import input_has_no_empty_value
from .mawlety_API import update_order_state_in_mawlety 
from .monitoring_API import delete_a_monitor_order_by_id, get_monitor_orders_by_carrier, update_a_monitor_order_by_id,add_afex_order_to_monitoring_phase
from .global_variables import AFEX_LOGIN_URL, AFEX_MONITOR_ORDER_TABLE_NAME, DELETE_MONITOR_ORDER_STATES, MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID



def load_cities_delgs_locs_postal_codes() : 
    with open("./cities_dels_locs_afex_v1_js.json","r") as f: 
        cities_delg_locs_postal_codes = json.loads(f.read())
        return cities_delg_locs_postal_codes

def load_driver(port=None,headless=False): 
    chrome_driver_path = ChromeDriverManager().install()
    chrome_options = Options()
    chrome_options.headless = headless
    
    if port : 
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    
    driver = webdriver.Chrome(chrome_driver_path,options=chrome_options,service_log_path='NUL')
    
    return driver 

# USED IN MULTIPLE SITUATIONS TO WAIT FOR AN ELEMENT TO EXIST GIVEN HIS CSS SELECTOR (OR A CUSTOM WAIT LIKE THE INPUT CASE)
def wait_for_loading(driver,element_selector,relogin=False,quitx=False,input=False): 
    # TRY TO LOCATE AN ELEMENT
    try : 
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, element_selector)) if not input else input_has_no_empty_value((By.CSS_SELECTOR, element_selector)) 
        )
    except Exception :
       
        # HANDLE THE EXCEPTION
        print("WE WERE WAITING FOR ONE MINUTE FOR THE WINDOW OR THE PAGE TO LOAD OR AN IMPUT TO BE EMPTY")

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





#cities_delgs_locs_postal_codes[city][delg][loc]
    
def wait_for_orders_table(driver):
    print("WAIT FOR ORDERS TABLE")
    existing_orders_len = 0 
    passed_seconds = 0 
    res = False 
    # NOTE :  I USED PANELS TO DO NOT MISTAKE IT WITH TABLE OF "Gestion du paiment"
    while True: 
        res = driver.execute_script("""
            let panels = document.querySelectorAll(".x-panel.x-grid.x-fit-item.x-panel-default")
            if(panels){
                let pre_manifest_panel = panels[0]
                if(pre_manifest_panel.querySelector("table.x-grid-table.x-grid-table-resizer")){
                    return {existing_orders_len:pre_manifest_panel.querySelectorAll('table.x-grid-table.x-grid-table-resizer tr').length -1 }
                }
            }
            return false 
        """)
        if res : 
            break 

        print("WAIT 2 MORE SECONDS FOR THE PRE MANIFEST ORDER TABLE TO LOAD")
        time.sleep(2)
        passed_seconds += 2 
        if passed_seconds == 10 : 
            print("NO ORDERS TO LOAD")
            return existing_orders_len 
    if res : 
        print("ORDERS ARE LOADED")
        return res['existing_orders_len']
        


def load_the_order_form(driver):
    # LAUNCH THE ORDER SENDER SOFTWARE
    driver.execute_script("document.querySelector('#envoi-shortcut').click()")
    # WAIT FOR ORDER SENDER SOFTWARE TO LOAD WITHIN A MINUTE OTHERWISE QUIT()  TO HANDLE THIS BUG
    wait_for_loading(driver,"add_bord",quitx=True)
    # WAIT FOR THE ORDER TABLE TO LOAD (TO DO NOT LET THE ORDER SOFTWARE BECOME ABOVE THE ORDER FORM WINDOW ONCE THE ORDERS TABLE IS LOADED )
    existing_orders_len = wait_for_orders_table(driver)
    # OPEN THE ORDER FORM 
    print("OPEN THE ORDER FORM")
    driver.execute_script("document.querySelector('#add_bord').click()")

    # WAIT FOR THE ORDER FORM TO LOAD WITHIN A MINUTE OTHERWISE QUIT() TO HANDLE THIS BUG
    wait_for_loading(driver,"input[name='societe_expediteur']",quitx=True,input=True)
    print("THE ORDER FORM IS LOADED")  
    return existing_orders_len





def initiate_search_carnet_adresse(driver):
    inp = driver.find_elements(By.NAME, 'search_carnet_adresse')[1]
    inp.send_keys("Ari")
    while not driver.execute_script("""
            let tables =  document.querySelectorAll('table.x-grid-table.x-grid-table-resizer')
            return tables.length > 0 && tables[tables.length-1].querySelector(".x-grid-cell-first").innerText == 'Ariana'
            """):
        print("WAIT 2 MORE SECONDS FOR THE TABLE TO APPEAR")
        time.sleep(2)

    driver.execute_script("""
        let tables =  document.querySelectorAll('table.x-grid-table.x-grid-table-resizer')
        let first_cell = tables[tables.length-1].querySelector(".x-grid-cell-first")
        let event = new MouseEvent('mousedown',{view:window,bubbles: true,
        cancelable: true})
        first_cell.dispatchEvent(event)
    """)

def fill_the_order_form(driver,order):
    initiate_search_carnet_adresse(driver)
    driver.execute_script("""
        let order = arguments[0] 

        let customer_name_inp = document.querySelector("input[name='nom_pre_destinataire']")
        customer_name_inp.value = `${order['customer_detail']['firstname']} ${order['customer_detail']['lastname']}`

        let tel_inp = document.querySelector("input[name='tel_destinataire']")
        tel_inp.value = order['address_detail']['phone_mobile']

        let address_inp = document.querySelector("textarea[name='adresse_destinataire']")
        address_inp.value = order['address_detail']['address1']

        let city_inp = document.querySelector("input[name='gouvernerat_destinataire']")
        city_inp.value = order['address_detail']['city']

        let delg_inp = document.querySelector("input[name='deleg_destinataire']")
        delg_inp.value = order['address_detail']['delegation']

        let loc_inp = document.querySelector("input[name='localite_destinataire']")
        loc_inp.value = order['address_detail']['locality'].split(" code postal")[0]

        let post_code_inp = document.querySelector("input[name='code_postal_destinataire']")
        post_code_inp.value = order['address_detail']['postal_code']

        let marchandise_inp = document.querySelector("input[name='marchandise']")
        let cart_products = order['cart_products']
        let marchandise_val = "" 
        cart_products.map((product,idx)=>{
            marchandise_val += `${product['quantity']} x ${product['name']}`
            if (idx+1 != cart_products.length){
                marchandise_val+= ","
            }
        })
        marchandise_inp.value = marchandise_val


        let ref_inp = document.querySelector("input[name='ref_destinataire']")
        ref_inp.value = order['id']

        let type_envoi_inp = document.querySelector("input[name='type_envoi_colis']")
        type_envoi_inp.value = 'Livraison à domicile'

        type_envoi_inp.click()
        let event = new MouseEvent('mousedown',{view:window,bubbles: true,
        cancelable: true})
        type_envoi_inp.parentElement.parentElement.dispatchEvent(event)

        let montant_contre_rembst_inp = document.querySelector("input[name='montant_contre_rembst']")
        montant_contre_rembst_inp.value = order['total_paid']
        
    """,order)
    # WAIT FOR THE EVENT HANDLER TO CLEAR THE PRICE 
    while driver.execute_script("""return document.querySelector('input[name="montant_contre_rembst"]').value != '' """) : 
        print("WAITING 2 MORE SECONDS FOR THE EVENT HANDLER CLEAR THE PRICE")
        time.sleep(2)

    # RESET THE PRICE AND SET PAYMENT TYPES
    driver.execute_script("""
        let total_paid = arguments[0] 
        let montant_contre_rembst_inp = document.querySelector("input[name='montant_contre_rembst']")
        montant_contre_rembst_inp.value = total_paid
       
        let mode_regl_inp = document.querySelectorAll("input[name='mode_regl']")[2]
        mode_regl_inp.value = 'Chèque ou espèces'
       
    """,order['total_paid'])

def save_order(driver,new_order=False):
    if new_order == False : 
        driver.execute_script("document.querySelector('#save_close .x-btn-inner').click()")
    else: 
        # CLICK SAVE AND NEW BUTTON
        driver.execute_script("document.querySelector('#save_new .x-btn-inner').click()")
        # WAIT ORDER FORM TO BE RESETED 
        while not driver.execute_script("""
                let customer_name_inp = document.querySelector("input[name='nom_pre_destinataire']")
                let company_name = document.querySelector("input[name='societe_expediteur']")
                return customer_name_inp.value== "" && company_name.value !=""
        """):
            info = driver.execute_script("""
                let customer_name_inp = document.querySelector("input[name='nom_pre_destinataire']").value
                let company_name = document.querySelector("input[name='societe_expediteur']").value
                return [customer_name_inp,company_name]
            """)
            print(f"customer_name_inp : {info[0]}")
            print(f"company_name : {info[1]}")
            print("WAIT 2 MORE SECONDS UNTIL THE ORDER FORM IS RESETED")
            time.sleep(2)
    

def manifest_orders(driver,expected_orders_len):
    # WAIT FOR THE SUBMITTED ORDERS TO APPEAR IN THE TABLE 
    print(f"expected_orders_len : {expected_orders_len}")
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
        print("WAIT 2 MORE SECONDS FOR THE SUBMITTED ORDERS TO APPEAR IN THE TABLE")
        time.sleep(2)

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

    # WAIT FOR THE PRINT MESSAGE BOX
    while not driver.execute_script("return document.querySelectorAll('.x-message-box').length && document.querySelectorAll('.x-message-box .x-window-body')[0].innerText.includes('Manifest Validé')") : 
        print("WAIT 2 MORE SECONDS FOR THE PRINT MESSAGE BOX TO LOAD")
        time.sleep(2)

    # CLICK NO TO NOT PRINT
    driver.execute_script("document.querySelectorAll('.x-message-box button')[2].click()")

def submit_orders(driver,orders,orders_submitter_obj):

    existing_orders_len =  load_the_order_form(driver)
    print(f"existing_orders_len : {existing_orders_len}")
    cities_delgs_locs_postal_codes = load_cities_delgs_locs_postal_codes()
    orders_len = len(orders)
    for idx,order in enumerate(orders): 
        print(f"WORKING ON SUBMITTING THE ORDER WITH ID : {order['id']}")

        orders_submitter_obj.state['progress']['current_order_id'] = order['id']
        orders_submitter_obj.save()

        # ADD FOR EACH ORDER HIS POSTAL CODE
        city =  order['address_detail']['city']
        delegation = order['address_detail']['delegation']
        locality = order['address_detail']['locality']
        order['address_detail']['postal_code'] = cities_delgs_locs_postal_codes[city][delegation][locality]

        fill_the_order_form(driver,order)
       
        if idx+1 != orders_len : 
            save_order(driver,new_order=True)
        else: 
            save_order(driver)

        add_afex_order_to_monitoring_phase(order)

        # INSCREASE submitted_orders_len TO THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress']['submitted_orders_len']  += 1 
        orders_submitter_obj.save()
    
    # START MANIFESTING
    # SET THE MANIFEST STATE TO THE ORDERS SUBMITTER
    print("START MANIFESTING")
    orders_submitter_obj.state['state'] = "MANIFESTING"
    orders_submitter_obj.save()

    # WAIT FOR THE SUBMITTED ORDERS TO APPEAR IN THE TABLE 
    expected_orders_len = existing_orders_len + len(orders)
    manifest_orders(driver,expected_orders_len)
    print("END SUBMITTIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIING ORDERS")
    


    
def submit_afex_orders(orders,orders_submitter_obj):

    print("LOAD THE DRIVER")
    driver = load_driver(headless=True) 
    print("LOGIN TO AFEX")
    login_to_afex(driver=driver)
    print("START SUBMITTING ORDERS")
    submit_orders(driver,orders,orders_submitter_obj)
    



def load_the_order_manager(driver=None):
    if not driver : 
        driver = globals()['driver']

    # LAUNCH THE ORDER SENDER SOFTWARE
    driver.execute_script("document.querySelector('#envoi-shortcut').click()")

    # WAIT FOR ORDER SENDER SOFTWARE TO LOAD WITHIN A MINUTE OTHERWISE QUIT()  TO HANDLE THIS BUG
    wait_for_loading(driver,"add_bord",quitx=True)



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
        'Livré':'Livré',
        'Retourne':'Retour',
        'annulé':'Annulé',
        'en attente':'Expédié',
    }
    for afex_state in afex_state_to_mawlety_state.keys() : 
        if afex_state in afex_order_state  : 
            return afex_state_to_mawlety_state[afex_state]

    




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

    # FOR EACH AFEX MONITOR ORDER CHECK IF THE STATE OF THE ORDER WAS UPDATED IF SO DO YOUR THING
    for afex_monitor_order in afex_monitor_orders : 

        # SET THE NEW current_order_id
        orders_monitoror_obj.state['progress']['current_order_id'] = afex_monitor_order.order_id
        orders_monitoror_obj.save()

        # AFEX ORDER STATE FROM DB 
        afex_monitor_order_state = afex_monitor_order.state

        # AFEX ORDER STATE FROM AFEX SITE  
        afex_order_state = orders_from_afex[str(afex_monitor_order.order_id)]

        # CONVERT IT TO MAW STATE
        afex_order_state = afex_state_to_mawlety_state_converter(afex_order_state) 

        #CHECK IF THE STATE OF THE CURRENT MONITOR ORDER WAS CHANGED
        if afex_monitor_order_state != afex_order_state  : 
            print("THERE IS A CHANGE")
            # IF THE NEW STATE IS ONE OF THE DELETE STATE DELETE THE ORDER FROM THE TABLE 
            if afex_order_state in DELETE_MONITOR_ORDER_STATES : 
                delete_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id)
            # OTHERWISE UPDATE THE AFEX MONITOR ORDER
            else:
                update_a_monitor_order_by_id('AFEX',afex_monitor_order.order_id,afex_order_state)


            # ADD THE CHANGED ORDER TO THE RESULTS

            # CHECK IF results KEYWORD EXIST OTHERWISE ADD IT 
            if orders_monitoror_obj.state.get('results') == None :
                orders_monitoror_obj.state['results'] = []

            # ADD THE CHANGED ORDER OBJ TO THE RESULT KEYWORD
            orders_monitoror_obj.state['results'].append({
                'order_id': afex_monitor_order.order_id,
                'carrier' : 'AFEX',
                'old_state' : afex_monitor_order.state,
                'new_state' : afex_order_state
            })
            orders_monitoror_obj.save()

            #UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
            #update_order_state_in_mawlety(afex_monitor_order.order_id,MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID[afex_order_state])
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

    submit_orders(driver,orders)
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