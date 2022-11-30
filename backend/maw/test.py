 # FOR EACH filtered_state_card 
    #   1- GO IT'S LINK 
    #   2- EXTRACT THEIR TRANSACTIONS ID
    #   3- FOR EACH LOXBOX MONITOR ORDER CHECK IF THE ORDER BELONG TO THE CARD STATE USING THE TRANSACTION ID IF SO THEN : 
    #           CHECK IF THE STATE OF THE LOXBOX MONITOR ORDER CHANGED IF SO :
    #               UPDATE THE STATE LOXBOX MONITOR ORDER 
    #               CHECK IF THE UPDATE DB IS TRUE IF SO : 
    #                   CHECK IF THE NEW STATE IN THE DELETE_MONITOR_ORDER_STATES IF SO  :
    #                       DELETE THE MONITOR ORDER FROM THE TABLE
    #                   ELESE : 
    #                       UPDATE THE MONITOR ORDER WITH THE NEW STATE 
    #               UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
    #   4- IF return_monitor_orders_updated == True
    #       return loxbox_monitor_orders
    #     
"""
for filtered_state_card in filtered_state_cards : 
    #1- GO IT'S LINK AND GET THE CORRESPONDING MAWLElY STATE OF THE CURRENT STATE CARD STATE ID TO COMPARE IT WITH STATES OF MONITOR ORDERS
    r = session.get(filtered_state_card['state_card_link'])
    new_mawlety_state = LOXBOX_STATE_ID_TO_MAWLETY_STATE_STR[filtered_state_card['state_card_state_id']]

    #2- EXTRACT THEIR TRANSACTIONS ID
    soup = BeautifulSoup(r.text,"html.parser")
    current_state_card_transactions_id = [el.text for el in soup.select('th > a')]

    #3- FOR EACH LOXBOX MONITOR ORDER CHECK IF THE ORDER BELONG TO THE CARD STATE USING THE TRANSACTION ID IF SO THEN : 
    for idx,loxbox_monitor_order in enumerate(loxbox_monitor_orders) :  
        if str(loxbox_monitor_order['transaction_id']) in current_state_card_transactions_id : 

            if new_mawlety_state != loxbox_monitor_order['state'] :
                
                #CHECK IF THE return_monitor_orders_updated IS FALSE IF SO : 
                if return_monitor_orders_updated == False  : 

                    #CHECK IF THE NEW STATE IN THE DELETE_MONITOR_ORDER_STATES IF SO  : DELETE THE MONITOR ORDER FROM THE TABLE
                    if new_mawlety_state in DELETE_MONITOR_ORDER_STATES : 
                        delete_a_monitor_order_by_id('LOXBOX',loxbox_monitor_order['order_id'])
                    # OTHERWISE UPDATE THE LOXBOX MONITOR ORDER
                    else: 
                        update_a_monitor_order_by_id('LOXBOX',loxbox_monitor_order['order_id'],new_mawlety_state)
                
                #UPDATE THE STATE OF THE ORDER IN MAWLATY.COM
                print("update state in mawlety")
                update_order_state_in_mawlety(loxbox_monitor_order['order_id'],MAWLETY_STR_STATE_TO_MAWLETY_STATE_ID[new_mawlety_state])
                
            # IF return_monitor_orders_updated == True RETURN loxbox_monitor_orders
            if return_monitor_orders_updated == True : 
                if new_mawlety_state != loxbox_monitor_order['state'] :
                    loxbox_monitor_order['state'] = new_mawlety_state
                return loxbox_monitor_orders 
            
            # REMOVE IT FROM loxbox_monitor_orders TO NOT WASTE TIME CHECKING IF HE BELONG TO OTHER CARD STATES 
            loxbox_monitor_orders.pop(idx)

            # BREAK OUT OF THE FUNCTION IF ALL loxbox_monitor_orders ARE POPPED OUT => WE CHECK THE STATE OF ALL THE ORDERS
            if len(loxbox_monitor_orders) == 0 : 
                return 
"""