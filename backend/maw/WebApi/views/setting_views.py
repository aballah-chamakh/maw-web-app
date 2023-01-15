from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Setting
from ..serializers import SettingSerializer 

@api_view(['GET'])
def get_setting(request):
    setting_obj = Setting.objects.first()
    ser = SettingSerializer(setting_obj)
    return Response(ser.data,status.HTTP_200_OK)


@api_view(['PUT'])
def update_setting(request):
    setting_part = request.data.get('setting_part')
    form_data = request.data.get('form_data')
    print(form_data)

    setting_obj = Setting.objects.first()

    if setting_part == 'afex' : 
        setting_obj.afex_email = form_data.get(setting_part+'Email').strip()
        setting_obj.afex_password = form_data.get(setting_part+'Password').strip()

    elif setting_part == 'loxbox' : 
        setting_obj.loxbox_email = form_data.get(setting_part+'Email').strip()
        setting_obj.loxbox_password = form_data.get(setting_part+'Password').strip()

    elif  setting_part == 'mawlety_api' : 
        setting_obj.mawlety_api_key = form_data.get('mawletyApiKey').strip()
    else : 
        setting_obj.afex_client_id = form_data.get('afexClientId')
        setting_obj.afex_api_key = form_data.get('afexApiKey').strip()

    setting_obj.save()

    return Response({'msg':'the setting was updated'},status.HTTP_200_OK)







