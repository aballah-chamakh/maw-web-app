import requests
from requests.exceptions import ConnectionError, RequestException ,HTTPError,Timeout,JSONDecodeError

class DolzayRequest  : 

    http_methods = {
        "GET": requests.get,
        "POST": requests.post,
        "PUT": requests.put,
        "DELETE": requests.delete,
    }

    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    REQUEST_ERROR = "REQUEST_ERROR"
    FORCIBLY_CLOSED_ERR_MSG = "An existing connection was forcibly closed by the remote host"
    TIMEOUT = 120

    def __init__(self,**kwargs):
        self.method = kwargs['method']
        self.header = kwargs['header']
        self.url = kwargs['url']
        self.body = kwargs.get('body')  
        self.context = kwargs.get('context')
        self.parameters = kwargs.get('parameters')
        self.additional_instructions = kwargs.get('additional_instructions')
        self.check_json = kwargs.get('check_json')
        self.order_action_obj = kwargs.get('order_action_obj')
        self.ignore_404 = kwargs.get('ignore_404')
        self.custom_unauthorization_err_handler = kwargs.get('custom_unauthorization_err_handler')

    def internet_or_website_err_handler(self,err_msg):
        print("internet_or_website_err_handler")

        self.order_action_obj.state['alert'] = {
            'alert_type' : 'error',
            'error_msg' : f"Votre connexion internet ou le site web {self.parameters['website']} ne fonctionne pas",
            'error_details' : err_msg,
            'error_context' : self.context,
            'instructions' : [
                "Vérifiez si votre connexion internet fonctionne.",
                f"Vérifiez si le site web {self.parameters['website']} fonctionne.",
                "Essayez la même action à nouveau.",
                "Si les/l' étape(s) précédente(s) n'ont/a pas résolu le problème, appelez l'équipe de support Dolzay au : 58671414.",
            ]
        }

        # ADD ADDITIONAL INSTRUCTIONS IF THEY EXIST 
        if additional_instructions and 'internet_or_website_err' in additional_instructions.keys():
            for instruction in additional_instuction['internet_or_website_err']
                order_action_obj.state['alert']['instructions'].insert(instruction['pos']-1,instruction['instruction'])
            order_action_obj.save()   

        self.order_action_obj.state['state']="FINISHED"
        self.order_action_obj.save()
        quit()


    def unexpected_err_handler(self,err_msg):
        # ADD THE DATA OF THE ALERT 
        self.order_action_obj.state['alert'] = {
            'alert_type' : 'error',
            'error_msg' :  f"Cette erreur est inattendue et survient généralement parce que le site web {self.parameters['website']} a modifié son système.",
            'error_details' : err_msg,
            'error_context' : self.context,
            'instructions' : [
                "Essayez la même action à nouveau.",
                "Si les/l' étape(s) précédente(s) n'ont/a pas résolu le problème, appelez l'équipe de support Dolzay au : 58671414."
            ]
        }

        # ADD ADDITIONAL INSTRUCTIONS IF THEY EXIST 
        if additional_instructions and 'unexpected_err' in additional_instructions.keys():
            for instruction in additional_instuction['unexpected_err']
                order_action_obj.state['alert']['instructions'].insert(instruction['pos']-1,instruction['instruction'])
            order_action_obj.save()    

        self.order_action_obj.state['state']="FINISHED"
        self.order_action_obj.save()
        quit()

    def slow_website_or_internet_err_handler(self,err_msg,is_website=False):
        # ADD THE DATA OF THE ALERT 
        self.order_action_obj.state['alert'] = {
            'alert_type' : 'error',
            'error_msg' :  f"Votre site web : {self.parameters['website']} est lent" if is_website else f"Votre site web : {self.parameters['website']} ou votre connexion internet est lent(e).",
            'error_details' : err_msg,
            'error_context' : self.context,
            'instructions' : [
                f"Essayez la même action plus tard lorsque le site web  : {self.parameters['website']} n'est pas surchargé." if is_website else f"Essayez la même action plus tard lorsque votre Internet est rapide et le site web  : {self.parameters['website']} n'est pas surchargé.",
                "Si les/l' étape(s) précédente(s) n'ont/a pas résolu le problème, appelez l'équipe de support Dolzay au : 58671414."
            ]
        }

        # ADD ADDITIONAL INSTRUCTIONS IF THEY EXIST 
        if additional_instructions and 'slow_website_or_internet_err' in additional_instructions.keys():
            for instruction in additional_instuction['slow_website_or_internet_err']
                order_action_obj.state['alert']['instructions'].insert(instruction['pos']-1,instruction['instruction'])
            order_action_obj.save()   

        self.order_action_obj.state['state']="FINISHED"
        self.order_action_obj.save()
        quit()

    def unauthorization_err_handler(self,err_msg):
        self.order_action_obj.state['alert'] = {
            'alert_type' : 'error',
            'error_msg' :  f"Les identifiants du site web {self.parameters['website']} sont invalides.",
            'error_context' : self.context,
            'instructions' : [
                f"Mettez à jour les identifiants du site web {self.parameters['website']}",
                "Si les/l' étape(s) précédente(s) n'ont/a pas résolu le problème, appelez l'équipe de support Dolzay au : 58671414."
            ]
        }

        # ADD ADDITIONAL INSTRUCTIONS IF THEY EXIST 
        if additional_instructions and 'unauthorization_err' in additional_instructions.keys():
            for instruction in additional_instuction['slow_website_or_internet_err']
                order_action_obj.state['alert']['instructions'].insert(instruction['pos']-1,instruction['instruction'])
            order_action_obj.save() 

        self.order_action_obj.state['state']="FINISHED"
        self.order_action_obj.save()
        quit()

    def no_orders_handler(self):
        self.order_action_obj.state['alert'] = {
            'alert_type' : 'info',
            'info_msg' :  f"Il n'y a pas de commandes à charger entre le {self.parameters['date_range']['start_date']} et le {self.parameters['date_range']['end_date']}."
        }
        self.order_action_obj.state['state']="FINISHED"
        self.order_action_obj.save()
        quit()


    def make_request(self):
        try : 

            res = self.http_methods[self.method](self.url,header=self.header,data=self.body,timeout=self.TIMEOUT)
            res.raise_for_status()
            if self.check_json : 
                data = r.json()
            return res

        except ConnectionError as ce : 
            err_msg = str(ce)
            forcibly_closed_err_msg = "An existing connection was forcibly closed by the remote host"
            if self.forcibly_closed_err_msg in err_msg : 
                self.slow_website_or_internet_err_handler(err_msg,is_website=True)
            else : 
                self.internet_or_website_err_handler(err_msg)

        except HTTPError as he :
            err_msg = str(he)
            if res.status_code == 401 :
                if self.custom_unauthorization_err_handler : 
                    self.custom_unauthorization_err_handler(self.order_action_obj,self.parameters['order_id'])
                self.unauthorization_err_handler(err_msg)
            elif self.ignore_404 and res.status_code == 404 :
                return res 
            else :
                self.unexpected_err_handler(err_msg)
    
        except Timeout as to : 
            err_msg = str(to)
            self.slow_website_or_internet_err_handler(err_msg)

        except RequestException as re : 
            err_msg = str(re)
            self.unexpected_err_handler(err_msg)
        
        except JSONDecodeError as jde : 
            err_msg = str(jde)
            self.no_orders_handler()
 
