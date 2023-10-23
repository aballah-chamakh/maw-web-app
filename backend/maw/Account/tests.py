from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse 
from Account.models import User ,CompanyProfile,CompanyOrderState
from Account.serializers import CompanyProfileSerializer 

class CompanyProfileTests(APITestCase):
    credentials = {'email':'user','password':'the_password'}
    def setUp(self):
        # CREATE A COMPANY PROFILE
        user_obj = User.objects.create_user(username='user',**self.credentials)
        company_profile_obj = CompanyProfile.objects.create(
            user=user_obj,
            api_base_url='http://localhost:8000',
            api_key='1234567890'
        )

        # CREATE SOME STATE 
        valid_state_obj = CompanyOrderState.objects.create(company=company_profile_obj,
                                         state_name='Valid',
                                         state_id = 5)
        processing_state_obj = CompanyOrderState.objects.create(company=company_profile_obj,
                                         state_name='processing',
                                         state_id = 10)

        # ASSIGN THE LOADING STATE AND THE POST SUBMIT STATE 
        company_profile_obj.loading_state = valid_state_obj # ID : 1
        company_profile_obj.post_submit_state = processing_state_obj # ID : 2
        company_profile_obj.save()



    def test_a_retreiving_company_profile(self):
        print("TEST RETREIVING COMPANY PROFILE")
        company_profile_api_url = api_reverse('Account:companyprofile-detail',kwargs={'pk':1})
        res = self.client.get(company_profile_api_url,format='json')
        print(res.content_type)
        print(res.data)
        print("END TEST RETREIVING COMPANY PROFILE")
        
        #"self.assertEqual(CompanyProfile.objects.all().count(),1)
    
    def test_b_updating_company_profile(self):
        print("TEST UPDATE COMPANY PROFILE PARITALLY")
        company_profile_api_url = api_reverse('Account:companyprofile-detail',kwargs={'pk':1})
        data = {
            'loading_state': 2,
            'post_submit_state': 1,
            'api_key' : '1010'
        }
        res = self.client.patch(company_profile_api_url,data,format='json')
        print(res.status_code)
        print(res.data)
        company_profile_obj = CompanyProfile.objects.first()
        print(CompanyProfileSerializer(company_profile_obj).data)
        print("END TEST UPDATE COMPANY PROFILE PARITALLY")
    
    def test_c_post_updating_company_profile(self):
        print("TEST POST UPDATE COMPANY PROFILE PARITALLY")
        company_profile_obj = CompanyProfile.objects.first()
        print(CompanyProfileSerializer(company_profile_obj).data)
        print("END POST TEST UPDATE COMPANY PROFILE PARITALLY")

    def test_access_token(self):
        print(" ========== TEST ACCESS TOKEN ===================")
        api_token_url = api_reverse('Account:token_obtain_pair')
        res = self.client.post(api_token_url,self.credentials,format='json')
        print(res.data)
        print(" ========== END TEST ACCESS TOKEN ===================")



        
