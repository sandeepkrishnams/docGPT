from django.utils import timezone

from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers
from users.utils import validate_username


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'is_active'
        ]


class UserSignUpSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        username = validate_username(validated_data['username'])
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=username
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        extra_kwargs = {
            'username': {'required': True, 'error_messages': {'required': 'username address is required'}},
            'email': {'required': False},
            'first_name': {'required': True, 'error_messages': {'required': 'first_name is required'}},
            'last_name': {"allow_null": True},
            'password': {'error_messages': {'required': 'Password is required'}}
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user is not None and user.is_active:
            user.last_login = timezone.now()
            user.save()

        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True, 'error_messages': {'required': 'first_name is required'}},
            'last_name': {"allow_null": True}
        }


class UserPasswordUpdateSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    token = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name',
                  'date_joined', 'last_login']

    # def to_representation(self, instance):
    #     if instance.is_superuser:
    #         return {}
    #     return super().to_representation(instance)
