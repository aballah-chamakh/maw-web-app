import json 
import pprint
from django.core.files import File
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse 
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from Account.models import CompanyProfile
from Common.tests import CommonTests
from .models import Carrier, CarrierStateConversion
from .serializers import CarrierSerializer,CarrierStateConversionSerializer
from .views import CarrierViewSet,CarrierStateConversionViewSet


class CarrierViewSetAPITestCase(APITestCase,CommonTests):
    VIEWSET_CLASS = CarrierViewSet
    EXPECTED_MODEL_CLASS = Carrier 
    EXPECTED_SERIALIZER_CLASS = CarrierSerializer 


    def setUp(self):
        # CREATE A COMPANY PROFILE
        self.create_company_profile()

        # ADD AUTHORIZATION HEADER TO THE CLIENT 
        self.add_authorization_header_to_the_client()
        
        # CREATE A CARRIER FOR THE TESTS 
        self.carrier = Carrier.objects.create(name='Test Carrier', api_base_url='http://example.com', api_key='test-key')
        self.carrier_state_converion = CarrierStateConversion.objects.create(
            carrier=self.carrier,
            carrier_state='State1',
            company_website_state='StateA'
        )
        # SET THE URL OF THE LIST AND CREATE ACTIONS 
        self.url = api_reverse('Carrier:carrier-list') # THIS URL WORKS FOR THE BOTH CREATE AND LIST 

    # THIS FUNCTION IS USED BY THE JWTAuthenticationBaseTest TO TEST AUTHORIZATION 
    # AND THE REASON WHY IT IS CUSTOM FOR EACH TEST CLASS BECAUSE EACH VIEWSET HAS HIS OWWS SPECIFUC MIXIN AND THOSE MIXINS HAVE THEIR OWN SPECIFIC PARAMERTERS 
    def authorization_request(self):
        return self.client.get(api_reverse('Carrier:carrier-list'))


    def test_list_carriers(self):
        # ADD AN ADDITIONAL CARRIER WITH CARRIER STATE CONVERSION TO TEST WITH A LIST WITH AT LEAST 2 ELEMENTS 
        carrier_2 = Carrier.objects.create(name='Test Carrier 2', api_base_url='http://example2.com', api_key='test-key2')
        carrier_state_converions_2 = CarrierStateConversion.objects.create(
            carrier=carrier_2,
            carrier_state='State2',
            company_website_state='StateB'
        )
        
        # SEND A CARRIER LIST REQUEST 
        response = self.client.get(self.url)

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DEFINE THE EXPECTED JSON RESPONSE DATA
        expected_json_response_data = { 
                            'count': 2,
                            'next': None,
                            'previous': None,
                            'results': [   
                                        {   
                                            'active': True,
                                            'api_base_url': 'http://example.com',
                                            'api_key': 'test-key',
                                            'carrier_state_conversions': None,
                                            'id': 1,
                                            'name': 'Test Carrier',
                                            'logo': 'http://testserver/media/carrier_logos/default_logo.png'
                                        },
                                        {  
                                            'active': True,
                                            'api_base_url': 'http://example2.com',
                                            'api_key': 'test-key2',
                                            'carrier_state_conversions': None,
                                            'id': 2,
                                            'name': 'Test Carrier 2',
                                            'logo': 'http://testserver/media/carrier_logos/default_logo.png'
                                        }
                        ]
        }

        # ASSERT THAT THE JSON RESPONSE DATA IS AS EXPECTED 
        json_response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_response_data, expected_json_response_data)

    def test_retrieve_carrier(self):
        # SEND A CARRIER RETREIVE REQUEST 
        response = self.client.get(api_reverse('Carrier:carrier-detail', args=[self.carrier.id]))
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DEFINE THE EXPECTED JSON RESPONSE DATA
        expected_json_response_data = {
                                        "id": 1,
                                        "carrier_state_conversions": {
                                            "count": 1,
                                            "next": None,
                                            "previous": None,
                                            "results": [
                                                {
                                                    "id": 1,
                                                    "carrier_state": "State1",
                                                    "company_website_state": "StateA",
                                                    "carrier": 1,
                                                }
                                            ],
                                        },
                                        "logo": "http://testserver/media/carrier_logos/default_logo.png",
                                        "name": "Test Carrier",
                                        "api_base_url": "http://example.com",
                                        "api_key": "test-key",
                                        "active": True,
                                        }

        # ASSERT THAT THE JSON RESPONSE DATA IS AS EXPECTED 
        json_response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_response_data, expected_json_response_data)


    def test_partial_update_carrier(self):
        # SEND A CARRIER PATCH REQUEST TO UPATE ONLY ONE FIELD
        data = {'api_key': 'new_api_key'}
        response = self.client.patch(api_reverse('Carrier:carrier-detail', args=[self.carrier.pk]), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE CARRIER 
        self.carrier.refresh_from_db()

        # USING THE SERIALIZER ASSERT THAT THE FIELD THIS PATICULAR CARRIER ROW IN THE DB WAS UPDATED 
        ser = CarrierSerializer(self.carrier,many=False)
        self.assertEqual(data['api_key'], ser.data['api_key'])


    def test_full_update_carrier(self):
         # SEND A CARRIER UPDATE REQUEST TO FULLY UPDATE THE CARRIER 
        data = {'api_base_url':'http://newexample.com', 'api_key':'new-test-key','active':True,
            'logo': ('comapny_logo.jpg', open('media/carrier_logos/default_logo.png', 'rb'), 'image/jpeg')
        }
        response = self.client.put(api_reverse('Carrier:carrier-detail', kwargs={'pk':self.carrier.pk}), data, format='multipart')
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE CARRRIER 
        self.carrier.refresh_from_db()

        # UPDATING THE DATA BECAUSE SOME FIELDS ARE JUST READ ONLY AND OTHER ARE JUST WRITE ONLY 
        data['id'] = self.carrier.id # BECAUSE THIS FIELD IS READ ONLY 
        data['logo'] =  self.carrier.logo.url # BECAUSE THE ORIGINAL VALUE IS BYTES 
        data['name'] =  self.carrier.name  # BECAUSE THIS FIELD IS READ ONLY 
        data['carrier_state_conversions'] =  response.data['carrier_state_conversions'] # BECAUSE THIS FIELD IS READ ONLY 

        # USING THE SERIALIZER ASSERT THAT THIS PATICULAR CARRIER ROW IN THE DB WAS UPDATED 
        ser = CarrierSerializer(self.carrier,many=False)
        self.assertEqual(data, ser.data)

    def test_bulk_activate_carriers_single(self):

        # DEACTIVATE THE CARRIER BECAUSE BY DEFAULT HE IS ACTIVE 
        self.carrier.active = False 
        self.carrier.save()

        # SEND AN ACTIVATION REQUEST FOR A SPECIFIC LIST OF CARRIERS 
        data = {'action': 'activate', 'carrier_ids': [self.carrier.pk]}
        response = self.client.patch(api_reverse('Carrier:carrier-bulk-action'), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE RESOONSE DATA IS AS EXPECTED 
        expected_response = {'res': 'success'}
        self.assertEqual(response.data, expected_response)

        # REFRESH THE CARRIER 
        self.carrier.refresh_from_db()

        # ASSERT THAT THE CARRIER IS ACTIVE NOW 
        self.assertTrue(self.carrier.active)

    def test_bulk_activate_carriers_many(self):
        # DEACTIVATE THE CARRIER BECAUSE BY DEFAULT HE IS ACTIVE 
        self.carrier.active = False 
        self.carrier.save()

        # CREATE AN ADDITONAL CARRIER FOR THE MANY TEST 
        carrier_2 = Carrier.objects.create(name='Test Carrier 2', api_base_url='http://example2.com', api_key='test-key2',
                                            active=False)

        # SEND AN ACTIVATION REQUEST FOR A SPECIFIC LIST OF CARRIERS 
        data = {'action': 'activate', 'carrier_ids': [self.carrier.pk,carrier_2.id]}
        response = self.client.patch(api_reverse('Carrier:carrier-bulk-action'), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE RESOONSE DATA IS AS EXPECTED 
        expected_response = {'res': 'success'}
        self.assertEqual(response.data, expected_response)

        # REFRESH THE CARRIERS
        self.carrier.refresh_from_db()
        carrier_2.refresh_from_db()

        # ASSERT THAT THE CARRIER IS ACTIVE NOW 
        self.assertTrue(self.carrier.active)
        self.assertTrue(carrier_2.active)

    def test_bulk_deactivate_carriers_single(self):

        # SEND A DEACTIVATION REQUEST FOR A SPECIFIC LIST OF CARRIERS 
        data = {'action': 'deactivate', 'carrier_ids': [self.carrier.pk]}
        response = self.client.patch(api_reverse('Carrier:carrier-bulk-action'), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE RESOONSE DATA IS AS EXPECTED 
        expected_response = {'res': 'success'}
        self.assertEqual(response.data, expected_response)

        # REFRESH THE CARRIER 
        self.carrier.refresh_from_db()

        # ASSERT THAT THE CARRIER IS INACTIVE NOW 
        self.assertFalse(self.carrier.active)

    def test_bulk_deactivate_carriers_many(self):
        # CREATE AN ADDITONAL CARRIER FOR THE MANY TEST 
        carrier_2 = Carrier.objects.create(name='Test Carrier 2', api_base_url='http://example2.com', api_key='test-key2')

        # SEND A DEACTIVATION REQUEST FOR A SPECIFIC LIST OF CARRIERS 
        data = {'action': 'deactivate', 'carrier_ids': [self.carrier.pk,carrier_2.id]}
        response = self.client.patch(api_reverse('Carrier:carrier-bulk-action'), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE RESOONSE DATA IS AS EXPECTED 
        expected_response = {'res': 'success'}
        self.assertEqual(response.data, expected_response)

        # REFRESH THE CARRIERS 
        self.carrier.refresh_from_db()
        carrier_2.refresh_from_db()

        # ASSERT THAT THE CARRIER IS INACTIVE NOW 
        self.assertFalse(self.carrier.active)
        self.assertFalse(carrier_2.active)




class CarrierStateConversionViewSetAPITestCase(APITestCase,CommonTests):
    VIEWSET_CLASS = CarrierStateConversionViewSet
    EXPECTED_MODEL_CLASS = CarrierStateConversion
    EXPECTED_SERIALIZER_CLASS = CarrierStateConversionSerializer 

    def setUp(self):
        # CREATE A COMPANY PROFILE
        self.create_company_profile()

        # ADD AUTHORIZATION HEADER TO THE CLIENT 
        self.add_authorization_header_to_the_client()

        # CREATE A CARRIER FOR THE TESTS 
        self.carrier = Carrier.objects.create(
            name='Test Carrier',
            api_base_url='http://example.com',
            api_key='test-key'
        )

        self.carrier_state_conversion = CarrierStateConversion.objects.create(
            carrier=self.carrier,
            carrier_state='State1',
            company_website_state='StateA'
        )

        # SET THE URL OF THE LIST AND CREATE ACTIONS 
        self.url = api_reverse('Carrier:carrierstateconversion-list')

    
    def authorization_request(self):
        return self.client.get(api_reverse('Carrier:carrierstateconversion-list'),{'carrier_id':self.carrier.id})


    def test_list_carrier_state_conversions(self):
        # CREATE AN ADDITIONAL CARRIER STATE COVERSION FOR TO HAVE A LIST OF AT LEAST TWO ELEMENTS 
        carrier_state_conversion_2 = CarrierStateConversion.objects.create(
            carrier=self.carrier,
            carrier_state='State_2',
            company_website_state='StateA_2'
        )
        # CREATE AN ADDITIONAL CARRIER STATE COVERSION THAT DOESN'T BELONG TO THE FIRST CARRIER TO TEST THE QUERY PARAM 'carrier_id'
        carrier_state_conversion_3 = CarrierStateConversion.objects.create(
            carrier=Carrier.objects.create(name='Test Carrier 2', api_base_url='http://example2.com', api_key='test-key2'),
            carrier_state='State_1x',
            company_website_state='StateA_1x'
        )


        # SEND A CARRIER STATE CONVERSION LIST REQUEST 
        response = self.client.get(self.url,{'carrier_id':self.carrier.id})

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # DEFINE THE EXCPECTED JSON RESPONSE DATA 
        expected_json_response_data = {
                                        "count": 2,
                                        "next": None,
                                        "previous": None,
                                        "results": [
                                            {
                                                "id": 1,
                                                "carrier_state": "State1",
                                                "company_website_state": "StateA",
                                                "carrier": 1,
                                            },
                                            {
                                                "id": 2,
                                                "carrier_state": "State_2",
                                                "company_website_state": "StateA_2",
                                                "carrier": 1,
                                            },
                                        ],
                                    }

        # ASSERT THAT THE JSON RESPONSE DATA IS AS EXPECTED 
        json_respone_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_respone_data,expected_json_response_data)

    def test_create_carrier_state_conversion(self):
        # SEND A CARRIER STATE CONVERSION CREATE REQUEST 
        data = {'carrier': self.carrier.id, 'carrier_state': 'State1xx', 'company_website_state': 'StateAxx'}
        response = self.client.post(self.url, data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # UPDATING THE DATA BECAUSE SOME FIELDS ARE JUST READ-ONLY AND OTHERS ARE JUST WRITE-ONLY 
        data['id'] = response.data['id'] # BECAUSE THIS FIELD IS READ-ONLY

        # USING THE SERIALIZER ASSERT THAT THE CREATED ROW IS EQUAL TO THE DATA 
        instance = CarrierStateConversion.objects.get(pk=response.data['id'])
        serializer = CarrierStateConversionSerializer(instance=instance)
        self.assertEqual(data, serializer.data)

    def test_patch_update_carrier_state_conversion(self): 

        # SEND A CARRIER STATE CONVERSION PATCH REQUEST TO UPDATE ONLY ONE FIELD
        data = {'carrier_state': 'UpdatedState'}
        response = self.client.patch(api_reverse('Carrier:carrierstateconversion-detail', args=[self.carrier_state_conversion.pk]), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE CARRIER STATE CONVERSION INSTANCE
        self.carrier_state_conversion.refresh_from_db()

        # USING THE SERIALIZER ASSERT THAT THE FIELD OF THIS PARTICULAR CARRIER STATE CONVERSION ROW IN THE DB WAS UPDATED 
        ser = CarrierStateConversionSerializer(self.carrier_state_conversion, many=False)
        self.assertEqual(data['carrier_state'], ser.data['carrier_state'])

    def test_full_update_carrier_state_conversion(self):

        # CREATE A CARRIER AND A CARRIER STATE CONVERSION 
        new_carrier = Carrier.objects.create(
            name='NEW Carrier',
            api_base_url='http://example.com',
            api_key='test-key'
        )

        # SEND A CARRIER STATE CONVERSION UPDATE REQUEST TO FULLY UPDATE THE CARRIER STATE CONVERSION
        data = {
            'carrier': new_carrier.id,
            'carrier_state': 'UpdatedState',
            'company_website_state': 'UpdatedWebsiteState'
        }
        response = self.client.put(api_reverse('Carrier:carrierstateconversion-detail', kwargs={'pk': self.carrier_state_conversion.pk}), data, format='json')
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE CARRIER STATE CONVERSION INSTANCE
        self.carrier_state_conversion.refresh_from_db()

        # UPDATING THE DATA BECAUSE SOME FIELDS ARE JUST READ-ONLY AND OTHERS ARE JUST WRITE-ONLY 
        data['id'] = self.carrier_state_conversion.id # BECAUSE THIS FIELD IS READ-ONLY

        # USING THE SERIALIZER ASSERT THAT TTHIS PARTICULAR CARRIER STATE CONVERSION ROW IN THE DB WAS FULLY UPDATED 
        ser = CarrierStateConversionSerializer(self.carrier_state_conversion, many=False)
        self.assertEqual(data, ser.data)

    def test_destroy_carrier_state_conversion(self):

        # SEND A CARRIER DELETE REQUEST 
        response = self.client.delete(api_reverse('Carrier:carrierstateconversion-detail', args=[self.carrier_state_conversion.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # CHECK IF THE CARRIER STATE CONVERSION WAS DELETED
        self.assertEqual(CarrierStateConversion.objects.count(), 0)

    def test_bulk_delete_carrier_state_conversions_single(self):

        # SEND A CARRIER BULK DELETE REQUEST 
        data = {'carrier_state_conversion_ids': [self.carrier_state_conversion.pk, ]}
        response = self.client.delete(api_reverse('Carrier:carrierstateconversion-bulk-delete'), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE RESPONSE DATA MATCHES THE EXPECTED RESPONSE
        expected_response = {'res': 'success'}
        self.assertEqual(response.data, expected_response)

        # CHECK IF THE CARRIER STATE CONVERSIONS WERE DELETED
        self.assertEqual(CarrierStateConversion.objects.count(), 0)

    def test_bulk_delete_carrier_state_conversions_many(self):

        # CREATE AND ADDITIONAL CARRIER STATE CONVERSION
        carrier_state_conversion_2 = CarrierStateConversion.objects.create(
            carrier=self.carrier,
            carrier_state='State_2',
            company_website_state='StateA_2'
        )

        # SEND A CARRIER BULK DELETE REQUEST 
        data = {'carrier_state_conversion_ids': [self.carrier_state_conversion.pk, carrier_state_conversion_2.id]}
        response = self.client.delete(api_reverse('Carrier:carrierstateconversion-bulk-delete'), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ASSERT THAT THE RESPONSE DATA MATCHES THE EXPECTED RESPONSE
        expected_response = {'res': 'success'}
        self.assertEqual(response.data, expected_response)

        # CHECK IF THE CARRIER STATE CONVERSIONS WERE DELETED
        self.assertEqual(CarrierStateConversion.objects.count(), 0)


    