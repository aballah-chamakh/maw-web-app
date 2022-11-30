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
            
afex_states = [
    "__ en attente d'enlevement",
    "__ en attente de livraison",
    "__ en cours de livraison",
    "__ en attente de livraison",
    '__ en attente de relivraison\n-->colis reporté à la demande du client' ,
   '__ en attente\n-->numéro erroné',
   'en attente de retour',
   'en cours de retour',
   '__ Livré Le 16/02/2022\n-->à payer / OP N° 202203816',
   'Retourne',
   '__ annulé\n-->client injoignable'
]

for fx_state in afex_states : 
    print(f"afex_state : {fx_state} CONVERTED TO maw_state : {afex_state_to_mawlety_state_converter(fx_state)}")