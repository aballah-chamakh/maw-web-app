# afex_API.py TRASH CODE 
""" 
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


