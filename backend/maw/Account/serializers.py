from rest_framework import serializers
from .models import CompanyProfile, CompanyOrderState

class CompanyOrderStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyOrderState
        fields = '__all__'

class CompanyProfileSerializer(serializers.ModelSerializer):
    company_order_states = serializers.SerializerMethodField()
    loading_state = CompanyOrderStateSerializer(many=False, read_only=True)
    post_submit_state = CompanyOrderStateSerializer(many=False, read_only=True)
    api_base_url = serializers.CharField(read_only=True)
    class Meta:
        model = CompanyProfile
        fields = '__all__'

    def get_company_order_states(self, obj):
        # Retrieve related CompanyWebsiteState objects
        company_order_states = CompanyOrderState.objects.filter(company=obj)
        # Serialize the related objects
        return CompanyWebsiteStateSerializer(company_order_states, many=True).data