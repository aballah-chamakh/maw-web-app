import json 
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse 
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from Account.models import User ,CompanyProfile,CompanyOrderState
from Account.serializers import CompanyProfileSerializer,CompanyOrderStateSerializer
from Account.views import CompanyProfileViewSet,CompanyOrderStateViewSet
from Common.tests import CommonTests

class CompanyProfileAPITestCase(APITestCase,CommonTests):
    VIEWSET_CLASS = CompanyProfileViewSet
    EXPECTED_MODEL_CLASS = CompanyProfile 
    EXPECTED_SERIALIZER_CLASS = CompanyProfileSerializer 

    def setUp(self):
        # CREATE A COMPANY PROFILE
        self.create_company_profile()

        # ADD AUTHORIZATION HEADER TO THE CLIENT 
        self.add_authorization_header_to_the_client()

        # CREATE COMPANY ORDER STATES 
        canceled_state =CompanyOrderState.objects.create(company=self.company_profile_obj,
                                         state_id=10,
                                         state_name='Annulé')
        delivered_state = CompanyOrderState.objects.create(company=self.company_profile_obj,
                                         state_id=5,
                                         state_name='Livré')


        # SET THE LOADING STATE AND THE POST SUBMIT STATE OF THE COMPANY PROFILE 
        self.company_profile_obj.loading_state = delivered_state
        self.company_profile_obj.post_submit_state = canceled_state
        self.company_profile_obj.save()


    # THIS FUNCTION IS USED BY THE JWTAuthenticationBaseTest TO TEST AUTHORIZATION 
    # AND THE REASON WHY IT IS CUSTOM FOR EACH TEST CLASS BECAUSE EACH VIEWSET HAS HIS OWWS SPECIFUC MIXIN AND THOSE MIXINS HAVE THEIR OWN SPECIFIC PARAMERTERS 
    def authorization_request(self):
        return self.client.get(api_reverse('Account:companyprofile-detail',kwargs={'pk':self.company_profile_obj.id}))

    def test_obtaining_access_and_refresh_token(self) : 
        self.client.credentials(HTTP_AUTHORIZATION='')
        company_cendentials = {'email':self.company_profile_data['email'],'password':self.company_profile_data['password']}
        response = self.client.post(api_reverse('Account:token_obtain_pair'),company_cendentials,format='json')
        self.assertEqual(['refresh','access'],list(response.data.keys()))

    def test_refreshing_access_and_refresh_token(self) : 
        self.client.credentials(HTTP_AUTHORIZATION='')
        refresh_token = {'refresh': str(RefreshToken.for_user(self.user_obj)) }
        response = self.client.post(api_reverse('Account:token_refresh'),refresh_token,format='json')
        self.assertEqual(['access','refresh'],list(response.data.keys()))

    def test_retrieve_company_profile(self) :
        # SEND A COMPANY PROFILE RETRIEVE REQUEST 
        response = self.client.get(api_reverse('Account:companyprofile-detail',kwargs={'pk':self.company_profile_obj.id}))
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DEFINE THE EXPECTED JSON RESPONSE DATA
        expected_json_response_data = {
            "id": 1,
            "company_order_states": {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {"id": 1, "state_id": 10, "state_name": "Annulé"},
                    {"id": 2, "state_id": 5, "state_name": "Livré"},
                ],
            },
            "api_base_url": "http://www.paraclic.com",
            "logo": "http://testserver/media/company_logos/logo_2.png",
            "api_key": "154876ddf41ds",
            "loading_state": 2,
            "post_submit_state": 1,
        }

        json_response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(json_response_data,expected_json_response_data)

    def test_partial_update_company_profile(self):
        # SET A NEW VALUE TO THE FIELD WE WANT UPDATE 
        new_data = {'api_key' : 'new_api_key'}
        
        # SEND A COMPANY PROFILE PATCH REQUEST 
        response = self.client.patch(api_reverse('Account:companyprofile-detail',kwargs={'pk':self.company_profile_obj.id}),new_data)
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE COMPANY PROFILE 
        self.company_profile_obj.refresh_from_db()

        # CHECK IF THE COMPANY PROFILE WAS UPDATED 
        self.assertEqual(self.company_profile_obj.api_key,new_data['api_key'])

    def test_full_update_company_profile(self): 
        # SET A NEW VALUE TO THE FIELDS I MUST UPDATE TO PERFORM FULL UPDATE
        new_data = {
            'logo': ('comapny_logo.jpg', open('media/company_logos/logo.png', 'rb'), 'image/jpeg'),
            'api_key':'new-test-key',
            'loading_state' :  1,
            'post_submit_state' :  2,
        }

        # SEND A COMPANY PROFILE PUT REQUEST 
        response = self.client.put(api_reverse('Account:companyprofile-detail',kwargs={'pk':self.company_profile_obj.id}),new_data)
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE COMPANY PROFILE 
        self.company_profile_obj.refresh_from_db()
        
        # FULLFILL THE NEW DATA WITH THE READ ONLY FIELDS OR IMAGE FIELDS FROM THE SERIALIZER
        ser = CompanyProfileSerializer(self.company_profile_obj)
        new_data['id'] = ser.data['id']
        new_data['logo'] = ser.data['logo']
        new_data['api_base_url'] = ser.data['api_base_url']
        new_data['company_order_states'] = ser.data['company_order_states']
        
        # CHECK IF THE COMPANY PROFILE WAS UPDATED 
        self.assertEqual(ser.data,new_data)


class CompanyOrderStateAPITestCase(APITestCase,CommonTests):
    VIEWSET_CLASS = CompanyOrderStateViewSet
    EXPECTED_MODEL_CLASS = CompanyOrderState 
    EXPECTED_SERIALIZER_CLASS = CompanyOrderStateSerializer 

    def setUp(self):
        # CREATE A COMPANY PROFILE
        self.create_company_profile()

        # ADD AUTHORIZATION HEADER TO THE CLIENT 
        self.add_authorization_header_to_the_client()

        # CREATE COMPANY ORDER STATES 
        self.canceled_state =CompanyOrderState.objects.create(company=self.company_profile_obj,
                                         state_id=10,
                                         state_name='Annulé')
        self.delivered_state = CompanyOrderState.objects.create(company=self.company_profile_obj,
                                         state_id=5,
                                         state_name='Livré')


        # SET THE LOADING STATE AND THE POST SUBMIT STATE OF THE COMPANY PROFILE 
        self.company_profile_obj.loading_state = self.delivered_state
        self.company_profile_obj.post_submit_state = self.canceled_state
        self.company_profile_obj.save()

    def authorization_request(self):
        return self.client.get(api_reverse('Account:companyorderstate-list'))

    def test_list_company_order_states(self):
        # SEND A COMPANY ORDER STATE LIST REQUEST 
        response = self.client.get(api_reverse('Account:companyorderstate-list'))

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # DEFINE THE EXCPECTED JSON RESPONSE DATA 
        expected_json_response_data = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {"id": 1, "state_id": 10, "state_name": "Annulé",},
                {"id": 2, "state_id": 5, "state_name": "Livré"},
            ],
        }

        # ASSERT THAT THE JSON RESPONSE DATA IS AS EXPECTED 
        json_respone_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_respone_data,expected_json_response_data)


    def test_retrieve_company_order_state(self):
        # SEND A CARRIER RETREIVE REQUEST 
        response = self.client.get(api_reverse('Account:companyorderstate-detail', kwargs={'pk':self.canceled_state.id}))
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DEFINE THE EXPECTED JSON RESPONSE DATA
        expected_json_response_data = {"id": 1, "state_id": 10, "state_name": "Annulé"}

        # ASSERT THAT THE JSON RESPONSE DATA IS AS EXPECTED 
        json_response_data = json.loads(response.content.decode('utf-8'))
        
        #print(f"json_response_data : {json_response_data}")
        self.assertEqual(json_response_data, expected_json_response_data)

    def test_create_company_order_state(self):
        # SEND A COMPANY ORDER STATE CREATE REQUEST 
        data = {'state_id': 20, 'state_name': 'Returned'}
        response = self.client.post(api_reverse('Account:companyorderstate-list'), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # GET THE NEWLY CREATED COMPANY ORDER STATE 
        new_company_order_state_obj = CompanyOrderState.objects.last()

        # ADD THE READ ONLY FIELDS TO THE DATA 
        data['id'] = new_company_order_state_obj.id 

        # CHECK IF A NEW COMPANY ORDER STATE WAS CREATED 
        serializer = CompanyOrderStateSerializer(new_company_order_state_obj)
        self.assertEqual(data, serializer.data)


    def test_patch_update_company_order_state(self): 

        # SEND A COMPANY ORDER STATE PATCH REQUEST TO UPDATE ONLY ONE FIELD
        data = {'state_id': 30}
        response = self.client.patch(api_reverse('Account:companyorderstate-detail', kwargs={'pk':self.delivered_state.id}), data, format='json')

        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE COMPANY ORDER STATE INSTANCE
        self.delivered_state.refresh_from_db()

        # CHECK IF THE THE COMPANY ORDER STATE WAS UPDATED 
        self.assertEqual(self.delivered_state.state_id, data['state_id'])

    def test_full_update_company_order_state(self):

        # SEND A COMPANY ORDER STATE UPDATE REQUEST TO FULLY UPDATE THE COMPANY ORDER STATE
        data = {'state_id': 100, 'state_name': 'Prepared'}

        response = self.client.put(api_reverse('Account:companyorderstate-detail', kwargs={'pk': self.delivered_state.id}), data, format='json')
        
        # ASSERT THAT THE STATUS CODE OF THE RESPONSE IS SUCCESSFUL
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # REFRESH THE COMPANY ORDER STATE INSTANCE
        self.delivered_state.refresh_from_db()

        # ADD THE READ ONLY FIELDS TO THE DATA 
        data['id'] = self.delivered_state.id # BECAUSE THIS FIELD IS READ-ONLY

        # CHECK IF THE THE COMPANY ORDER STATE WAS UPDATED 
        serializer = CompanyOrderStateSerializer(self.delivered_state)
        self.assertEqual(data, serializer.data)

    def test_destroy_company_order_state(self):

        # SEND A CARRIER DELETE REQUEST 
        response = self.client.delete(api_reverse('Account:companyorderstate-detail', kwargs={'pk': self.delivered_state.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # CHECK IF THE COMPANY ORDER STATE WAS DELETED
        self.assertEqual(CompanyOrderState.objects.filter(id=self.delivered_state.id).count(), 0)





    



    







        













    






    



        
