from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # I SHOULD UPDATE THIS CODE WHEN I ADD THE EMPLOYE PROFILE 
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        #token['company_profile_id'] =  user.companyprofile.id
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer