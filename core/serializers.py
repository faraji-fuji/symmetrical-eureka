from rest_framework import serializers

from core.models import MyUser, Building, Floor, Office


class RegisterMyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model =  MyUser
        fields = ['username', 'email', 'password']

class GetMyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        # fields = ['username', 'password', 'email', 'first_name', 'last_name', 'is_superuser', 'is_visitor', 'is_checked_in']
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"

    
class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = "__all__"


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = "__all__"

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
