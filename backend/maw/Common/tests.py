from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from Account.models import CompanyProfile

class JWTAuthenticationTests : 

    company_profile_data = {
        'username' : 'Paraclic',
        'email' : 'paraclic@gmail.com' , 
        'password' : 'paraclic1234'
    }

    def create_company_profile(self) : 
        User = get_user_model()
        self.user_obj = User.objects.create_user(**self.company_profile_data)
        self.company_profile_obj = CompanyProfile.objects.create(user=self.user_obj,api_base_url='http://www.paraclic.com',api_key='154876ddf41ds')
    
    def add_authorization_header_to_the_client(self) : 
        token = str(AccessToken.for_user(self.user_obj))
        self.client.credentials(HTTP_CONTENT_TYPE='application/json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_authenticated_user_with_company_profile(self) : 
        response = self.authorization_request()
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_authenticated_user_without_company_profile(self) : 
        self.company_profile_obj.delete()
        response = self.authorization_request()
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user(self) : 
        self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.authorization_request()
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

class ViewSetAttributesTests: 

    def test_viewset_attributes(self):
        
        # ASSERT THAT THE MODEL CLASS OF QUERYSET ATTRIBUTE OF THE VIEWSET CLASS IS THE EXPECTED ONE
        self.assertEqual(self.VIEWSET_CLASS.queryset.model,self.EXPECTED_MODEL_CLASS)
        
        # ASSERT THAT THE SERIALIZER CLASS OF THE VIEWSET CLASS IS THE EXPECTED ONE
        self.assertEqual(self.VIEWSET_CLASS.serializer_class,self.EXPECTED_SERIALIZER_CLASS)
        
        # ASSERT THAT THE MODEL CLASS OF THE SERIALIZER CLASS OF THE VIEWSET CLASS IS THE EXPECTED ONE
        self.assertEqual(self.VIEWSET_CLASS.serializer_class.Meta.model,self.EXPECTED_MODEL_CLASS)


class CommonTests(JWTAuthenticationTests,ViewSetAttributesTests):
    pass 