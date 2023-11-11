from rest_framework import serializers
from maw.CustomPagination import CustomPagination
from .models import CompanyProfile, CompanyOrderState

class CompanyOrderStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyOrderState
        exclude = ('company',)
        

class CompanyProfileSerializer(serializers.ModelSerializer):
    company_order_states = serializers.SerializerMethodField()
    api_base_url = serializers.CharField(read_only=True)
    paginator = CustomPagination()

    class Meta:
        model = CompanyProfile
        exclude = ('user',)

    def get_company_order_states(self, company_profile_obj):
        # ENSURE THAT THE request and view objects exist in the context 
        request  = self.context.get('request')   
        view = self.context.get('view')
        
        if not request or not view :
            return None
        
        # GRAB THE COMPANY ORDER STATE OF THE CURRENT COMPANY  
        qs = company_profile_obj.companyorderstate_set.all()

        # ADD PAGINATION TO THE RESULTS
        page = self.paginator.paginate_queryset(qs,request)
        ser = CompanyOrderStateSerializer(page,many=True)
        data = {
            'count' :  self.paginator.page.paginator.count,
            'next' : self.paginator.get_next_link(),
            'previous' : self.paginator.get_previous_link(),
            'results' : ser.data
        }

        # BECAUSE THE REQUEST IS FOR THE COMPANY PROFILE WE NEED REPLACE 'companyprofiles' BY 'company_order_states' IN URLS OF THE PAGINATION
        if data['next'] : 
            data['next'] = data['next'].replace('companyprofiles','company_order_states')

        if data['previous'] : 
            data['previous'] = data['previous'].replace('companyprofiles','company_order_states')

        return data
