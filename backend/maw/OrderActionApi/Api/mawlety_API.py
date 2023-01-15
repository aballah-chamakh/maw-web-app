import requests
import json 
from datetime import datetime,timedelta
import xml.etree.ElementTree as ET
import time 
from .global_variables import HEADERS, MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID
from .global_functions import is_it_for_loxbox




MAWLATY_API_BASE_URL = "https://mawlety.com/api"

def load_cities_delegations(): 
    with open('cities_delegation.json','r') as f :
        cities_delegations = json.loads(f.read())
    return cities_delegations

# TODO : UPDATE THE THE WAY WE GRAB ORDERS WITH DISPLAY
def grab_maw_orders(orders_loader_id,nb_of_days_ago=0,state=MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID['Validé']):

    from WebApi.models import OrderAction
    orders_loader_obj = OrderAction.objects.get(id=orders_loader_id)

    HEADERS['Output-Format'] = "JSON"
    
    ## REQUEST ORDERS 
    
    # PREP REQUEST ORDERS  PARAMS
    end_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=nb_of_days_ago)).strftime("%Y-%m-%d")
    fields_to_collect_from_the_order = str(['id','total_paid','id_carrier','transaction_id','address_detail','customer_detail','cart_products','current_state']).replace("'","")

    # PREP REQUEST ORDERS URL
    orders_base_endpoint = "/orders/"
    orders_filter_endpoint = orders_base_endpoint + f"?filter[invoice_date]=[{start_date},{end_date}]&"
    orders_filter_endpoint += f"filter[current_state]=[{state}]&"
    orders_filter_endpoint += f"display={fields_to_collect_from_the_order}"
    print(orders_filter_endpoint)

    # MAKE THE REQUEST 
    r = requests.get(f"{MAWLATY_API_BASE_URL+orders_filter_endpoint}",headers=HEADERS)
    print(r.status_code)

    # HANDLE REQUEST ERROR
    if not r : 
        print(" NO ORDERS TO BE COLLECTED")
        orders_loader_obj.state['state']= "FINISHED"
        orders_loader_obj.state['orders']= []
        orders_loader_obj.state['canceled'] = True 
        orders_loader_obj.save()
        return 

    # HANDLE JSON ERROR
    if not r.json() : 
        orders_loader_obj.state['state']= "FINISHED"
        orders_loader_obj.state['orders']= []
        orders_loader_obj.state['canceled'] = True 
        orders_loader_obj.save()
        return 

    orders = r.json()['orders']

    if len(orders) > 0 : 
        orders_loader_obj.state['orders']  = []
        orders_loader_obj.state['orders_selected_all'] = True #FOR THE ORDERS SET THEM ALL SELECTED 
        # SET THE INITIAL PROGRESS STATE OF GRABBING THE ORDERS 
        orders_loader_obj.state['progress'] = {'current_order_id':orders[0]['id'],'grabbed_orders_len':0,'orders_to_grab_len':len(orders)}
        orders_loader_obj.save()

        # DECODE FROM STRING THE JSON OF THE VALUES OF THE FOLLOWING KEYS address_detail,customer_detail,cart_products
        for order in orders : 
            # SET THE CURRENT ORDER ID 
            orders_loader_obj.state['progress']['current_order_id'] = order['id']
            orders_loader_obj.save()


            # DECODE FROM STRING TO JSON 
            order['address_detail'] = json.loads(order['address_detail'])
            order['address_detail']['phone_mobile'] = order['address_detail']['phone_mobile'][:8]
            
            order['customer_detail'] = json.loads(order['customer_detail'])
            #order['customer_detail']['firstname'] = 'test'
            #order['customer_detail']['lastname'] = 'test'
            order['cart_products'] = json.loads(order['cart_products'])

            # SET THE CARRIER AND THE SELECTED KEY 
            order['carrier'] = 'LOXBOX' if is_it_for_loxbox(order['address_detail']['city'],order['address_detail']['delegation'],order['address_detail']['locality']) else 'AFEX' 
            order['selected'] = True 

            # APPEND THE ORDER 
            orders_loader_obj.state['orders'].append(order)

            # INCREASE THE GRABBED ORDERS LEN
            orders_loader_obj.state['progress']['grabbed_orders_len'] += 1
            
            orders_loader_obj.save()
    else : 
        orders_loader_obj['orders'] = []

    # SET THE FINISH STATE    
    orders_loader_obj.state['state'] = 'FINISHED'
    orders_loader_obj.save()

    del HEADERS['Output-Format']


def update_order_state_in_mawlety(order_id,order_state_str):
   
    
    # GET THE ORDER DATA IN XML 
    orders_base_endpoint = f"/orders/{order_id}"
    r = requests.get(MAWLATY_API_BASE_URL+orders_base_endpoint,headers=HEADERS)
    order_data = r.content.decode()

    
    # UPDATE THE ORDER CURRENT STATE
    root = ET.fromstring(order_data)
    order_tag = root[0]

    current_state = order_tag.find('current_state')
    current_state.text = MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID[order_state_str]

    transaction_id = order_tag.find('transaction_id')
    order_tag.remove(transaction_id)

    address_detail = order_tag.find('address_detail')
    order_tag.remove(address_detail)

    customer_detail = order_tag.find('customer_detail')
    order_tag.remove(customer_detail)

    cart_products = order_tag.find('cart_products')
    order_tag.remove(cart_products)

    
    # PUT THE UPDATE ORDER DATA
    HEADERS['Output-Format'] = "JSON"
    while True :
        r = requests.put(MAWLATY_API_BASE_URL+orders_base_endpoint,data=ET.tostring(root),headers=HEADERS)
        if r.status_code == 200 : 
            del HEADERS['Output-Format']
            return 
        print(f"WHILE TRYING TO UPDATE THE STATE OF THE ORDER ID :{order_id} THE FOLLOWING ERROR HAPPENED  : {r.json()} , WE WILL TRY AGAIN IN 2 SECONDS")
        time.sleep(2)

# from OrderActionApi.Api.mawlety_API import update_order_state_in_mawlety
# update_order_state_in_mawlety(608,'Expédié')