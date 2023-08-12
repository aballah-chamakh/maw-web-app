import requests
import json 
from datetime import datetime,timedelta
import xml.etree.ElementTree as ET
import time 
from .global_variables import HEADERS, MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID
from .global_functions import is_it_for_loxbox




MAWLATY_API_BASE_URL = "https://mawlety.com/api"

def is_phone_number_valid(phone_number):
    print(f"{phone_number} || {len(phone_number)} || {phone_number.isdigit()}")
    # REMOVE WHITE SPACES 
    phone_number = phone_number.replace(" ","")
    print(f"{phone_number} || {len(phone_number)} || {phone_number.isdigit()}")
    return len(phone_number) == 8 and phone_number.isdigit()

# TODO : UPDATE THE THE WAY WE GRAB ORDERS WITH DISPLAY
def grab_maw_orders(orders_loader_id,date_range,state=MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID['Validé']):

    from WebApi.models import OrderAction
    orders_loader_obj = OrderAction.objects.get(id=orders_loader_id)
    orders_loader_obj.state['orders']= []
    orders_loader_obj.state['invalid_orders'] = []
    orders_loader_obj.save()
    
    HEADERS['Output-Format'] = "JSON"
    
    ## REQUEST ORDERS 
    
    # PREP REQUEST ORDERS  PARAMS
    # INSCREASE THE END DATE BY ONE DATE 
    date_range['end_date'] = (datetime.strptime(date_range['end_date'], '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")
    date_range['start_date'] = datetime.strptime(date_range['start_date'], '%Y-%m-%d').strftime("%Y-%m-%d")
    #(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    # start_date = date_range['start_date']  #(datetime.today() - timedelta(days=nb_of_days_ago)).strftime("%Y-%m-%d")
    fields_to_collect_from_the_order = str(['id','reference','total_paid','id_carrier','transaction_id','address_detail','cart_products','current_state','date_add']).replace("'","")

    # PREP REQUEST ORDERS URL
    orders_base_endpoint = "/orders/"
    orders_filter_endpoint = orders_base_endpoint + f"?filter[date_add]=[{date_range['start_date']},{date_range['end_date']}]&"
    orders_filter_endpoint += f"filter[current_state]=[{state}]&"
    orders_filter_endpoint += f"display={fields_to_collect_from_the_order}&"
    orders_filter_endpoint += f"date=1"

    print(orders_filter_endpoint)
    print(HEADERS)

    # MAKE THE REQUEST 
    r = None 
    try : 
        r = requests.get(f"{MAWLATY_API_BASE_URL+orders_filter_endpoint}",headers=HEADERS)
        content_type = r.headers.get('Content-Type')
        if content_type:
            charset = content_type.split('charset=')[-1]
            print('Charset:', charset)
    except Exception as e :
        orders_loader_obj.state['state']= "FINISHED"
        orders_loader_obj.state['server_request_exception_error'] = 'THE FOLLOWING SERVER REQUEST ERROR HAPPENED WHILE THE GABBING THE VALID ORDERS FROM MAWLETY.COM : \n'
        orders_loader_obj.state['server_request_exception_error'] += str(e)+' ,'
        orders_loader_obj.state['server_request_exception_error'] += 'PLEASE FIX YOUR INTERNET CONNECTION'
        orders_loader_obj.save()
        return

    print(r.status_code)

    if r.status_code == 401 : 
        orders_loader_obj.state['state']= "FINISHED"
        orders_loader_obj.state['unauthorization_error'] = 'INVALID_MAWLETY_API_KEY' 
        orders_loader_obj.save()
        return
    print(r.content)
    # HANDLE JSON ERROR => EMPTY ARRAY
    if not r.json() : 
        
        print("JSON ERROR")
        print(r.text)
        orders_loader_obj.state['state']= "FINISHED"
        orders_loader_obj.save()
        return 
    
    orders = json.loads(r.content.decode('utf-8'))['orders']

    

    print(f"LEN ORDERS  : {len(orders)} || START ORDER ID   : {orders[0]['id']} || END ORDER ID : {orders[-1]['id']}")

    orders_loader_obj.state['orders']  = []
    if len(orders) > 0 : 
       
        orders_loader_obj.state['invalid_orders'] = []
        orders_loader_obj.state['orders_selected_all'] = True #FOR THE ORDERS SET THEM ALL SELECTED 
        # SET THE INITIAL PROGRESS STATE OF GRABBING THE ORDERS 
        orders_loader_obj.state['progress'] = {'current_order_id':orders[0]['id'],'grabbed_orders_len':0,'orders_to_grab_len':len(orders),'carrier':''}
        orders_loader_obj.save()

        # DECODE FROM STRING THE JSON OF THE VALUES OF THE FOLLOWING KEYS address_detail,customer_detail,cart_products
        for order in orders : 
         
            # DECODE FROM STRING TO JSON THE VALUE OF THE address_detail
            order['address_detail'] = json.loads(order['address_detail'])
            x = order['address_detail']['address1']
            # TRIM AND CAPITALIZE CITIES AND DELEGATIONS
            order['address_detail']['city'] = order['address_detail']['city'].title().strip()
            #order['address_detail']['delegation'] = order['address_detail']['delegation'].title().strip()
            
            # CHECK IF THE ORDER IS LOXBOX AND GRAB THE INVALID FIELDS OF THE ORDER
            is_it_loxbox,invalid_fields = (True,[],) if order['transaction_id'] else is_it_for_loxbox(order['address_detail']['city'],order['address_detail']['delegation'],order['address_detail']['locality'])

            # UPDATE THE PROGRESS OF THE current_order_id AND THE carrier
            orders_loader_obj.state['progress']['current_order_id'] = order['id']
            orders_loader_obj.state['progress']['carrier'] = 'LOXBOX' if is_it_loxbox else 'AFEX' if len(invalid_fields)==0 else ''
            orders_loader_obj.save()
            
            # SET THE CARRIER OF THE ORDER 
            order['carrier'] = orders_loader_obj.state['progress']['carrier']

            # CHANGE THE KEY OF THE DATE (AND GRAB ONLY THE DATE)
            order['created_at'] = order['date_add'].split(' ')[0]
            del order['date_add']
        
            # CHECK IF THE PHONE NUMBER IS NOT VALID , IF SO ADD IT TO INVALID FIELDS 
            if not is_phone_number_valid(order['address_detail']['phone_mobile']) : 
                invalid_fields.append('phone_mobile')
            
            # IF WE HAVE ANY INVALID FIELD APPEND THE ORDER TO THE INVALID ORDERS ARRAY 
            if len(invalid_fields)  > 0 :
                orders_loader_obj.state['invalid_orders'].append({'order_id':order['id'],'created_at':order['created_at'],'invalid_fields':invalid_fields})
            else :# OTHERWISE TO THE ORDERS ARRAY

                # DECODE FROM STRING TO JSON OTHER KEYS 
                order['cart_products'] = json.loads(order['cart_products'])

                # SET THE ORDER AS SELECTED  
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
    
    if r.status_code == 401 :
        return  r.status_code

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


    cart_products = order_tag.find('cart_products')
    order_tag.remove(cart_products)

    
    # PUT THE UPDATE ORDER DATA
    HEADERS['Output-Format'] = "JSON"
    while True :
        r = requests.put(MAWLATY_API_BASE_URL+orders_base_endpoint,data=ET.tostring(root),headers=HEADERS)
        if r.status_code == 200 : 
            del HEADERS['Output-Format']
            return 
        elif r.status_code == 401 :
            return  r.status_code
        print(f"WHILE TRYING TO UPDATE THE STATE OF THE ORDER ID :{order_id} THE FOLLOWING ERROR HAPPENED  : {r.json()} , WE WILL TRY AGAIN IN 2 SECONDS")
        time.sleep(2)

# from OrderActionApi.Api.mawlety_API import update_order_state_in_mawlety
# update_order_state_in_mawlety(608,'Expédié')