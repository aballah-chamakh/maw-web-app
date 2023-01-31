from WebApi.models import Setting


setting_obj = Setting.objects.first()

MAWLETY_AUTHORIZATION_TOKEN = setting_obj.mawlety_api_key

LOXBOX_LOGIN_CREDENTIAL  = {
    'username' : setting_obj.loxbox_email,
    'password' : setting_obj.loxbox_password
}

LOXBOX_API_CREDENTIAL  = {
    'api_key' : setting_obj.loxbox_api_key
}

AFEX_LOGIN_CREDENTIALS  = {
    'email' : setting_obj.afex_email , 
    'password' : setting_obj.afex_password
}

AFEX_API_CREDENTIALS = {
    'client_id': setting_obj.afex_client_id,
    'api_key' : setting_obj.afex_api_key
}

