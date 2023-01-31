# afex_API.py TRASH CODE 
""" 
    while True :
        # SEND THE MANIFEST REQUEST 
        r = afex_logged_session.post("http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/manifest",data=orders_to_manifest)
        # CHECK IF THE MANIFEST DIDN'T WORK 
        if not ('success' in r.text and r.json()['success'] == True) : 
            # NOTE : TO IMPROVE THIS PROCESS CHECK IF THE SUCCESS RESPONSE MESSAGE CHANGED
            # IF WE ALREADY UPDATED THE AFEX LOGGED SESSION RAISE AN EXPCEPTION ERROR
            if afex_logged_session_updated : 
                raise_an_exception_error(orders_submitter_obj,'THE_MANIFEST_REQUEST_NOT_WORKING')
                 
            
            # CHECK IF THE PROBLEM IS FROM THE AUTHORIZATION AND UPDATE THE AFEX LOGGED SESSION 
            afex_logged_session,status_code = get_afex_logged_session()   
            # HANDLE AN UNAUTHORIZATION ERROR IF IT EXIST 
            if status_code == 401 : 
                raise_a_unathorization_error(orders_submitter_obj,'INVALID_AFEX_CREDENTIALS_WHILE_MANIFESTING')
            
            # SET THE AFEX LOGGED SESSION UPDATED 
            afex_logged_session_updated = True 
        else : 
            break 
def load_cities_delgs_locs_postal_codes() : 
    with open("./cities_dels_locs_afex_v1_js.json","r") as f: 
        cities_delg_locs_postal_codes = json.loads(f.read())
        return cities_delg_locs_postal_codes

def refresh_and_load_the_order_manager(driver):
    # DISABLE THE BEFORE UNLOAD POPUP
    driver.execute_script(""
        window.onbeforeunload = null;
        window.onunload = null;
    "")

    # REFRESH THE PAGE
    driver.refresh()

    # WAITING FOR THE DASHBOARD TO APPEAR AFTER THE REFRESH
    wait_for_loading(driver,"envoi-shortcut")
    
    # LAUNCH THE ORDER MANAGER SOFTWARE 
    print("LAUNCH THE ORDER MANAGER SOFTWARE")
    driver.execute_script("document.querySelector('#envoi-shortcut').click()")
    
    # WAIT FOR ORDER MANAGER SOFTWARE TO BE LOADED 
    wait_for_loading(driver,"add_bord",quitx=True)


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
   
    driver.execute_script(""
        let credentials = arguments[0] ;

        let email_inp = document.querySelector("input[name='user_name']") 
        let password_inp = document.querySelector("input[name='user_password']")
        let login_btn = document.querySelector('.x-toolbar-item .x-btn-inner')

        email_inp.value = credentials.email
        password_inp.value  = credentials.password        

        login_btn.click() ""
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
def get_afex_logged_session_cookies() : 
    driver = load_driver()
    login_to_afex(driver=driver)
    return driver.get_cookies()


def waiting_for_loading_pre_manifest_orders_recursively(driver,expected_orders_len) : 
    TIMEOUT_SECONDS = 120
    passed_seconds = 0
    # NOTE :  I USED PANELS TO DO NOT MISTAKE IT WITH TABLE OF "Gestion du paiment"
    while not driver.execute_script(""
    let expected_orders_len = arguments[0] 
    let panels = document.querySelectorAll(".x-panel.x-grid.x-fit-item.x-panel-default")
        if(panels){
            let pre_manifest_panel = panels[0]
            if(pre_manifest_panel.querySelector("table.x-grid-table.x-grid-table-resizer")){
                return pre_manifest_panel.querySelectorAll('table.x-grid-table.x-grid-table-resizer tr').length -1 == expected_orders_len
            }
        }
        return false 
    "",expected_orders_len) :
        if passed_seconds == TIMEOUT_SECONDS : 
            refresh_and_load_the_order_manager(driver)
            waiting_for_loading_pre_manifest_orders_recursively(driver,expected_orders_len)
            break 
        print("WAIT 2 MORE SECONDS FOR THE SUBMITTED ORDERS TO APPEAR IN THE TABLE")
        time.sleep(2)
        passed_seconds += 2 

def fitlter_orders_manager_by_date_range(driver,orders) : 
    date_range = get_orders_date_range(orders)
    # SET THE DATE RANGE IN THE "SEND" TAB 
    driver.execute_script(""
        let date_range = arguments[0]
        document.querySelector('#date_start input').value = date_range['start_date']
        document.querySelector('#date_end input').value = date_range['end_date']
    "",date_range)

    # CLICK ON THE ORDER MANAGER TAB (IN THIS WAY WILL LOAD THE DATE RANGE NEEDED WITHOUT CLICKING ON THE SEARCH BTN)
    driver.execute_script("document.querySelector('.x-tab-bar .x-box-inner').childNodes[1].click()")

    # WAIT FOR THE ORDER MANAGER PANEL TO LOAD THE ORDERS TABLE
    while driver.execute_script(""
        let order_manager_panel = document.querySelectorAll(".x-panel-body.x-grid-body.x-panel-body-default.x-panel-body-default.x-layout-fit")[1]; 
        return order_manager_panel.classList.contains('x-masked')
        "") :
        print("WAIT 2 MORE SECONDS FOR THE ORDER MANAGER TABLE TO LOAD")
        time.sleep(2)
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
    orders_from_afex = driver.execute_script(""
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
    "") 

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
  
def get_pre_manifest_orders(driver_cookies): 

    request_cookies = {}
    for cookie in driver_cookies : 
        request_cookies[cookie['name']] = cookie['value'] 
    # GRAB ORDERS 
    r = requests.get("http://afex.smart-delivery-systems.com/webgesta/index.php/expeditionb/expedition_list?station=Info%40mawlety.com&client_id=136614&is_prestataire_marketplace=0&is_vendeur_marketplace=0&page=1&start=0&limit=1000000",cookies=request_cookies)
    return r.json()['records']

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
    driver.execute_script(""
        let order_table = document.querySelectorAll('table.x-grid-table.x-grid-table-resizer')[0]
        let event = new MouseEvent('mousedown',{view:window,bubbles: true,
            cancelable: true})
        order_table.querySelectorAll(".x-grid-cell-first").forEach(el=>{el.firstChild.firstChild.dispatchEvent(event)})
        document.querySelector('#imp_bord').nextElementSibling.click()
    "")    

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
        # GRAB EXISTING PRE MANIFEST ORDERS LEN 

def wait_for_orders_table(driver):
    print("WAIT FOR THE PRE MANIFEST ORDER TABLE TO LOAD")
    # GRAB PRE MANIFEST ORDERS
    existing_orders_len = 0 
    orders = get_pre_manifest_orders(driver=driver)

    # CHECK IF WE HAVE PRE MANIFEST ORDERS 
    if orders  : 
        existing_orders_len = len(orders)
        # KEEP WAITING FOR EVER UNTIL THE TABLE OF ORDERS TO APPEAR BECAUSE WE ARE SURE PRE MANIFEST ORDERS EXIST
        # NOTE :  I USED PANELS TO DO NOT MISTAKE IT WITH TABLE OF "Gestion du paiment"
        while not driver.execute_script(""
                let panels = document.querySelectorAll(".x-panel.x-grid.x-fit-item.x-panel-default")
                if(panels){
                    let pre_manifest_panel = panels[0]
                    if(pre_manifest_panel.querySelector("table.x-grid-table.x-grid-table-resizer")){
                        return true
                    }
                }
                return false 
            ""):

            print("WAIT 2 MORE SECONDS FOR THE PRE MANIFEST ORDER TABLE TO LOAD")
            time.sleep(2)

    return existing_orders_len

# QUIT TO SUBMIT THE ORDER (IN THE CASE OF HE WASN'T CREATED) AND THE OTHER ORDERS IN THE NEXT ORDERS SUBMITTER 
#orders_submitter_obj.state['state'] = "FINISHED"
#orders_submitter_obj.save()
#print(f"QUITING ON THE ORDER WITH THE ID  : {order['id']}")
#driver.quit()
#quit() 


info = driver.execute_script(
let customer_name_inp = document.querySelector("input[name='nom_pre_destinataire']").value
let company_name = document.querySelector("input[name='societe_expediteur']").value
return [customer_name_inp,company_name]
)
print(f"customer_name_inp : {info[0]}")
print(f"company_name : {info[1]}")

def load_the_order_form(driver):
    print("LAUNCH THE ORDER MANAGER SOFTWARE")
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

def initiate_search_carnet_adresse(driver,orders_submitter_obj):

    def load_the_search_carnet_adresse_table() :
        MAX_SECONDS_TO_WAIT = 180
        passed_seconds = 0 
        # SET "Ari" IN THE search_carnet_adresse FIELD 
        inp = driver.find_elements(By.NAME, 'search_carnet_adresse')[1]
        inp.send_keys("Ari")
        
        # WAITING FOR THE INITIATE_SEARCH_CARNET_ADRESSE TABLE TO APPEAR
        while not driver.execute_script(""
                let tables =  document.querySelectorAll('table.x-grid-table.x-grid-table-resizer')
                return tables.length > 0 && tables[tables.length-1].querySelector(".x-grid-cell-first").innerText == 'Ariana'
                ""):
            # HANDLE THE TIMEOUT
            if passed_seconds == MAX_SECONDS_TO_WAIT : 
                refresh_and_load_the_order_manager(driver,load_order_form=False)
                load_the_search_carnet_adresse_table(driver,orders_submitter_obj)
                break 

            print("WAIT 2 MORE SECONDS FOR THE INITIATE_SEARCH_CARNET_ADRESSE TABLE TO APPEAR")
            time.sleep(2)
            passed_seconds += 2 

    load_the_search_carnet_adresse_table()
    
    # SELECT ARIANA 
    driver.execute_script(""
        let tables =  document.querySelectorAll('table.x-grid-table.x-grid-table-resizer')
        let first_cell = tables[tables.length-1].querySelector(".x-grid-cell-first")
        let event = new MouseEvent('mousedown',{view:window,bubbles: true,
        cancelable: true})
        first_cell.dispatchEvent(event)
    "")

def fill_the_order_form(driver,order,orders_submitter_obj):
    initiate_search_carnet_adresse(driver,orders_submitter_obj)
    driver.execute_script(""
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

        let marchandise_val = "" 
        order['cart_products'].map((product,idx)=>{
            marchandise_val += `${product['quantity']} x ${product['name']}`
            if (idx+1 != order['cart_products'].length){
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
        
    "",order)
    # WAIT FOR THE EVENT HANDLER TO CLEAR THE PRICE 
        print("WAITING 2 MORE SECONDS FOR THE EVENT HANDLER CLEAR THE PRICE")
        time.sleep(2)

    # RESET THE PRICE AND SET PAYMENT TYPES
    driver.execute_script(""
        let total_paid = arguments[0] 
        let montant_contre_rembst_inp = document.querySelector("input[name='montant_contre_rembst']")
        montant_contre_rembst_inp.value = total_paid
       
        let mode_regl_inp = document.querySelectorAll("input[name='mode_regl']")[2]
        mode_regl_inp.value = 'Chèque ou espèces'
       
    "",order['total_paid'])

def was_this_order_created(driver,order_id): 


    # GRAB THE COOKIES FROM THE DRIVER 
    driver_cookies = driver.get_cookies()
    request_cookies = {}
    for cookie in driver_cookies : 
        request_cookies[cookie['name']] = cookie['value'] 

    # GRAB ORDERS 
    orders = get_pre_manifest_orders(driver=driver)
    if orders : 
        orders = list(reversed(orders[-5:]))
        # CHECK IF THIS ORDER EXIST 
        for order in orders  : 
            if order['ref_destinataire'] == str(order_id) : 
                return True 

    return  False 


def save_order(driver,order,new_order=False):
    MAX_SECONDS_TO_WAIT = 300
    passed_seconds = 0 
    # SAVE THE LAST ORDER 
    if new_order == False : 
        driver.execute_script("document.querySelector('#save_close .x-btn-inner').click()")
        # WAIT FOR THE ORDER TO BE CREATED 
        while not was_this_order_created(driver,order['id']) : 
            # HANDLE THE TIMEOUT
            if passed_seconds == MAX_SECONDS_TO_WAIT : 
                # RETURN ORDER WAS NOT CREATED 
                return False 

            print("WAIT 5 SECONDS MORE FOR THE LAST ORDER TO BE CREATED IN AFEX")
            time.sleep(5)
            passed_seconds += 5

    # SAVE THE CURRENT ORDER AND WAIT FOR THE FORM TO BE RESETED FOR THE NEXT ORDER
    else: 
        # CLICK SAVE AND NEW BUTTON
        driver.execute_script("document.querySelector('#save_new .x-btn-inner').click()")
        # WAIT ORDER FORM TO BE RESETED 
        while not driver.execute_script(""
                let customer_name_inp = document.querySelector("input[name='nom_pre_destinataire']")
                let company_name = document.querySelector("input[name='societe_expediteur']")
                return customer_name_inp.value== "" && company_name.value !=""
        ""):
            # HANDLE TIMEOUT 
            if passed_seconds == MAX_SECONDS_TO_WAIT : 
                # REFRESH AND LOAD THE ORDER FORM
                refresh_and_load_the_order_manager(driver,load_order_form=True)
                
                # CHECK IF THIS ORDER WAS CREATED 
                return was_this_order_created(driver,order['id']) 

            print("WAIT 2 MORE SECONDS UNTIL THE ORDER FORM IS RESETED")
            time.sleep(2)
            passed_seconds += 2 

    return True 

def submit_order_old(driver,order,orders_submitter_obj,order_idx,orders_len) :
    print(f"FILL THE FORM OF THE ORDER WITH ID : {order['id']}")
    fill_the_order_form(driver,order,orders_submitter_obj)
    
    print(f"SAVE THE ORDER WITH ID : {order['id']}")

    is_created = save_order(driver,order,new_order=True if order_idx+1 != orders_len else False)
    if not is_created : 
        submit_order_old(driver,order,orders_submitter_obj,order_idx,orders_len) 


def submit_orders(driver,orders,orders_submitter_obj):
    print("START SUBMITTING ORDERS TO AFEX ")
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

        submit_order_old(driver,order,orders_submitter_obj,idx,orders_len)

        print("ADD AFEX TO MONITROTING PHASE")        
        add_afex_order_to_monitoring_phase(order)

        # INSCREASE submitted_orders_len TO THE ORDERS SUBMITTER
        orders_submitter_obj.state['progress']['submitted_orders_len']  += 1 
        orders_submitter_obj.save()

        # WAIT 3 SECONDS FOR EACH ORDER SUBMITTED TO NOT THROTTLE THE AFEX SERVER 
        if idx+ 1 != len(orders) :
            print("WAIT 3 SECONDS BETWEEN EACH ORDER")
            time.sleep(3)

    
    # START MANIFESTING
    # SET THE MANIFEST STATE TO THE ORDERS SUBMITTER
    print("START MANIFESTING")
    #orders_submitter_obj.state['state'] = "MANIFESTING"
    #orders_submitter_obj.save()
    expected_orders_len = existing_orders_len + len(orders)
    manifest_orders(driver,expected_orders_len)

    print("END SUBMITTIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIING ORDERS")
    
"""


# TRASH CODE OF loxbox_api.py 
"""
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

"""
# TRASH CODE OF mawlety_api.py
"""
def load_cities_delegations(): 
    with open('cities_delegation.json','r') as f :
        cities_delegations = json.loads(f.read())
    return cities_delegations
"""