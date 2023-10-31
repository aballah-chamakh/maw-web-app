import json 
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse 
from rest_framework import status
from .models import Carrier, CarrierStateConversion
from .serializers import CarrierSerializer,CarrierStateConversionSerializer


# Create your tests here.


class CarrierViewSetTests(APITestCase):
    def setUp(self):
        self.carrier = Carrier.objects.create(name='Test Carrier', api_base_url='http://example.com', api_key='test-key')
        self.url = api_reverse('Carrier:carrier-list') # THIS URL WORKS FOR THE BOTH CREATE AND LIST 

    def test_list_carriers(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deserialize the response JSON
        response_data = response.data
        
        # Serialize the queryset to compare
        serializer = CarrierSerializer(instance=Carrier.objects.all(), many=True)
        self.assertEqual(response_data, serializer.data)

    def test_retrieve_carrier(self):
        response = self.client.get(api_reverse('Carrier:carrier-detail', args=[self.carrier.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data

        # Serialize the specific instance to compare
        serializer = CarrierSerializer(instance=self.carrier)
        self.assertEqual(response_data, serializer.data)

    def test_patch_update_carrier(self):
        data = {'api_key': 'new_api_key'}
        response = self.client.patch(api_reverse('Carrier:carrier-detail', args=[self.carrier.pk]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the carrier state conversion was updated
        self.carrier.refresh_from_db()
        ser = CarrierSerializer(self.carrier,many=False)

        self.assertEqual(data['api_key'], ser.data['api_key'])


    def test_full_update_carrier(self):
        data = {'api_base_url':'http://newexample.com', 'api_key':'new-test-key','active':True}
        
        response = self.client.put(api_reverse('Carrier:carrier-detail', kwargs={'pk':self.carrier.pk}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the carrier state conversion was updated
        self.carrier.refresh_from_db()
        ser = CarrierSerializer(self.carrier,many=False)

        data['id'] = self.carrier.id 
        data['logo'] =  self.carrier.logo.url 
        data['name'] =  self.carrier.name 
        print(f'ser : {ser.data}')
        print(f'data : {data}')
        self.assertEqual(data, ser.data)

    def test_bulk_activate_carriers(self):
        self.carrier.active = False 
        self.carrier.save()
        data = {'action': 'activate', 'carrier_ids': [self.carrier.pk]}
        response = self.client.patch(api_reverse('Carrier:carrier-bulk-action'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the JSON response matches the expected response
        expected_response = {'res': 'success'}
        self.assertEqual(json.loads(response.content), expected_response)

        # Check if the carriers were activated
        self.carrier.refresh_from_db()
        self.assertTrue(self.carrier.active)

    def test_bulk_deactivate_carriers(self):

        data = {'action': 'deactivate', 'carrier_ids': [self.carrier.pk]}
        response = self.client.patch(api_reverse('Carrier:carrier-bulk-action'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the JSON response matches the expected response
        expected_response = {'res': 'success'}
        self.assertEqual(json.loads(response.content), expected_response)

        # Check if the carriers were deactivated
        self.carrier.refresh_from_db()
        self.assertFalse(self.carrier.active)




class CarrierStateConversionViewSetTests(APITestCase):
    
    def setUp(self):
        # Create a Carrier for related tests
        self.carrier = Carrier.objects.create(name='Test Carrier', api_base_url='http://example.com', api_key='test-key')
  

        # Set the URL for the CarrierStateConversionViewSet  THIS URL WORKS FOR THE BOTH CREATE AND LIST 
        self.url = api_reverse('Carrier:carrierstateconversion-list')

    def test_list_carrier_state_conversions(self):
        CarrierStateConversion.objects.create(carrier=self.carrier,carrier_state='carrier_state_a',
                                              company_website_state = 'company_website_state_a')    
        CarrierStateConversion.objects.create(carrier=self.carrier,carrier_state='carrier_state_a',
                                              company_website_state = 'company_website_state_a')    
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Deserialize the response JSON
        response_data = response.data

        # Serialize the queryset to compare
        serializer = CarrierStateConversionSerializer(CarrierStateConversion.objects.all(), many=True)
        self.assertEqual(response_data, serializer.data)

    def test_create_carrier_state_conversion(self):
        data = {'carrier': self.carrier.id, 'carrier_state': 'State1', 'company_website_state': 'StateA'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Deserialize the response JSON
        response_data = response.data

        # Serialize the created instance to compare
        instance = CarrierStateConversion.objects.get(pk=response_data['id'])
        serializer = CarrierStateConversionSerializer(instance=instance)
        self.assertEqual(response_data, serializer.data)

    def test_patch_update_carrier_state_conversion(self):
        carrier_state_conversion = CarrierStateConversion.objects.create(carrier=self.carrier, carrier_state='State1', company_website_state='StateA')
        
        data = {'carrier_state': 'UpdatedState'}
        response = self.client.patch(api_reverse('Carrier:carrierstateconversion-detail', args=[carrier_state_conversion.pk]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # Check if the carrier state conversion was updated
        carrier_state_conversion.refresh_from_db()
        ser = CarrierStateConversionSerializer(carrier_state_conversion,many=False)

        self.assertEqual(data['carrier_state'], ser.data['carrier_state'])


    def test_full_update_carrier_state_conversion(self):
        new_carrier = Carrier.objects.create(name='NEW Carrier', api_base_url='http://example.com', api_key='test-key')
        carrier_state_conversion = CarrierStateConversion.objects.create(carrier=self.carrier, carrier_state='State1', company_website_state='StateA')
        
        data = {'carrier':new_carrier.id,'carrier_state': 'UpdatedState','company_website_state':'UpdatedWebsiteState'}
        response = self.client.put(api_reverse('Carrier:carrierstateconversion-detail', args=[carrier_state_conversion.pk]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # Check if the carrier state conversion was updated
        carrier_state_conversion.refresh_from_db()
        ser = CarrierStateConversionSerializer(carrier_state_conversion,many=False)

        data['id'] = carrier_state_conversion.id
        self.assertEqual(data, ser.data)


    def test_destroy_carrier_state_conversion(self):
        # CREATE A NEW CARRIER STATE CONVERSION
        carrier_state_conversion = CarrierStateConversion.objects.create(carrier=self.carrier, carrier_state='State1', company_website_state='StateA')
        
        # DELETE THE NEW CARRIER STATE CONVERSION
        response = self.client.delete(api_reverse('Carrier:carrierstateconversion-detail', args=[carrier_state_conversion.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check if the carrier state conversion was deleted
        self.assertEqual(CarrierStateConversion.objects.count(), 0)

    def test_bulk_delete_carrier_state_conversions(self):
        carrier_state_conversion_1 = CarrierStateConversion.objects.create(carrier=self.carrier, carrier_state='State1', company_website_state='StateA')
        carrier_state_conversion_2 = CarrierStateConversion.objects.create(carrier=self.carrier, carrier_state='State1', company_website_state='StateA')

        data = {'carrier_state_conversion_ids': [carrier_state_conversion_1.pk,carrier_state_conversion_2.pk]}
        response = self.client.delete(api_reverse('Carrier:carrierstateconversion-bulk-delete'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the JSON response matches the expected response
        expected_response = {'res': 'success'}
        self.assertEqual(json.loads(response.content), expected_response)

        # Check if the carrier state conversion was deleted
        self.assertEqual(CarrierStateConversion.objects.count(), 0)


    