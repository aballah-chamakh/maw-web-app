import json 
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse 
from Common.tests import CommonTests
from .models import Notification
from .serializers import NotificationSerializer 
from .views import NotificationViewSet


# Create your tests here.

class NotificationViewSetAPITestCase(APITestCase,CommonTests):
    VIEWSET_CLASS = NotificationViewSet
    EXPECTED_MODEL_CLASS = Notification 
    EXPECTED_SERIALIZER_CLASS = NotificationSerializer 

    def setUp(self):
        # CREATE A COMPANY PROFILE
        self.create_company_profile()

        # ADD AUTHORIZATION HEADER TO THE CLIENT 
        self.add_authorization_header_to_the_client()

        # CREATE NOTIFICATIONS TO TEST WITH 
        Notification.objects.create(type='Success',info={'msg':'you had successfully submitted 5 orders !!'})
        Notification.objects.create(type='Error',info={'msg':'there is no internet connection !!'})
        Notification.objects.create(type='Error',info={'msg':'this previous action may result in a inconsistent results !!'})

    # THIS FUNCTION IS USED BY THE JWTAuthenticationBaseTest TO TEST AUTHORIZATION 
    # AND THE REASON WHY IT IS CUSTOM FOR EACH TEST CLASS BECAUSE EACH VIEWSET HAS HIS OWWS SPECIFUC MIXIN AND THOSE MIXINS HAVE THEIR OWN SPECIFIC PARAMERTERS 
    def authorization_request(self):
        return self.client.get(api_reverse('Notification:notification-list'))

    def update_notification_datetimes(self,expected_notification_data,actual_notification_data) : 
        self.assertEqual(len(expected_notification_data),len(actual_notification_data))
        if 'results' in actual_notification_data.keys() : 
            for i in range(len(actual_notification_data['results'])) : 
                expected_notification_data['results'][i]['created_at'] = actual_notification_data['results'][i]['created_at']
        else : 
            expected_notification_data['created_at'] = actual_notification_data['created_at']

    def test_list_notifications(self):
        # SEND A CARRIER LIST REQUEST 
        response = self.client.get(api_reverse('Notification:notification-list'))

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DEFINE THE EXPECTED JSON RESPONSE DATA
        expected_json_response_data = {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "created_at": "13:19:19 07/11/23",
                    "type": "Success",
                    "info": {"msg": "you had successfully submitted 5 orders !!"},
                    "well_read": False,
                },
                {
                    "id": 2,
                    "created_at": "13:19:19 07/11/23",
                    "type": "Error",
                    "info": {"msg": "there is no internet connection !!"},
                    "well_read": False,
                },
                {
                    "id": 3,
                    "created_at": "13:19:19 07/11/23",
                    "type": "Error",
                    "info": {
                        "msg": "this previous action may result in a inconsistent results !!"
                    },
                    "well_read": False,
                },
            ],
        }
    

        # ASSERT THAT THE JSON RESPONSE DATA IS AS EXPECTED 
        json_response_data = json.loads(response.content.decode('utf-8'))
        self.update_notification_datetimes(expected_json_response_data,json_response_data) # BECAUSE THE created_at AT THE JSON RESPOSE DATA WILL NOT BE THE SAME IN THE EXPECETED JSON DATA
        self.assertEqual(json_response_data, expected_json_response_data)



    def test_retrieve_notification(self):
        # SEND A NOTIFICATION RETREIVE REQUEST 
        response = self.client.get(api_reverse('Notification:notification-detail', kwargs={'pk' :1}))
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DEFINE THE EXPECTED JSON RESPONSE DATA
        expected_json_response_data = {
            "id": 1,
            "created_at": "14:55:24 07/11/23",
            "type": "Success",
            "info": {"msg": "you had successfully submitted 5 orders !!"},
            "well_read": False,
        }

        # ASSERT THAT THE JSON RESPONSE DATA IS AS EXPECTED         
        json_response_data = json.loads(response.content.decode('utf-8'))
        self.update_notification_datetimes(expected_json_response_data,json_response_data) # BECAUSE THE created_at FIELD AT THE JSON RESPOSE DATA WILL NOT BE THE SAME IN THE EXPECETED JSON DATA
        self.assertEqual(json_response_data, expected_json_response_data)



    def test_mark_as_read_single(self):
        # DEFINE THE IDS OF NOTIFICATIONS I WANT TO MARK AS READ
        data = {'notification_ids': [1]}

        # SEND A NOTIFICATION MARK AS READ REQUEST 
        response = self.client.put(api_reverse("Notification:notification-mark-as-read"), data, format='json')
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE NOTIFICATION WAS MARKED AS READ      
        notification_obj = Notification.objects.get(id=1)
        self.assertEqual(notification_obj.well_read, True)

    def test_mark_as_read_many(self):
        # DEFINE THE IDS OF NOTIFICATIONS I WANT TO MARK AS READ
        data = {'notification_ids': [1,2]}

        # SEND A NOTIFICATION MARK AS READ REQUEST 
        response = self.client.put(api_reverse("Notification:notification-mark-as-read"), data, format='json')
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE NOTIFICATIONs WERE MARKED AS READ      
        notification_1_obj = Notification.objects.get(id=1)
        notification_2_obj = Notification.objects.get(id=2)
        self.assertEqual(notification_1_obj.well_read, True)
        self.assertEqual(notification_2_obj.well_read, True)

    def test_mark_as_read_with_empty_notification_ids(self):
        # DEFINE AN EMPTY NOTIFICATION IDS  
        data = {'notification_ids': []}
        
        # SEND A NOTIFICATION MARK AS READ REQUEST 
        response = self.client.put(api_reverse("Notification:notification-mark-as-read"), data, format='json')
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS A BAD REQUEST 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mark_as_read_with_no_notification_ids_key(self):
        # DEFINE THE BODY DATA WITHOUT THE 'notification_ids' KEY 
        data = {}
        
        # SEND A NOTIFICATION MARK AS READ REQUEST 
        response = self.client.put(api_reverse("Notification:notification-mark-as-read"), data, format='json')
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS A BAD REQUEST 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


