from dataclasses import field
from pyexpat import model

from Authentication import settings
from .models import Register 
from rest_framework import serializers
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import password_validation 
from django.utils.translation import gettext_lazy as _

class UserSerializers(serializers.ModelSerializer):
    class Meta :
        model = Register
        fields = "__all__"


class RegisterSerializers(serializers.ModelSerializer):  

    class Meta:
        model=Register
        fields=['user_name','first_name','last_name','bio','interests','email','ph_no','date_of_birth','password']  
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self,validated_data):
        customUser=Register.objects.create_user(validated_data['email'],validated_data['user_name']
            ,validated_data['interests'],validated_data['first_name'],validated_data['password'])
        return customUser

class RegisterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Register
        fields=['user_name','first_name','last_name','bio','interests','ph_no','date_of_birth','profile_pic_name']
    def update(self, instance, validated_data):
        instance.user_name=validated_data.get('user_name',instance.user_name)
        instance.first_name=validated_data.get('first_name',instance.first_name)
        instance.last_name=validated_data.get('last_name',instance.last_name)
        instance.date_of_birth=validated_data.get('date_of_birth',instance.date_of_birth)
        instance.interests=validated_data.get('interests',instance.interests)
        instance.bio=validated_data.get('bio',instance.bio)
        instance.ph_no=validated_data.get('ph_no',instance.ph_no)
        instance.save()
        return instance



class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    # username = serializers.CharField(
    #     max_length=255, min_length=3, read_only=True)

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = Register.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = Register
        fields = ['email', 'password' , 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = Register.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        if filtered_user_by_email.exists() == False:
            raise AuthenticationFailed(
                detail='Invalid email id. Please check it out.')

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        # if not user.is_verified:
        #     raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'username': user.user_name,
            'first_name' : user.first_name,
            'tokens': user.tokens
        }

        # return super().validate(attrs)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    } 


class ResetPasswordEmailSentSerializers(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        field = ['email']


class ResetPasswordSerializers(serializers.Serializer):
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
        "password_requirements" : _("Password did not match with minimum password validation Requirements")
    }
    new_password1 = serializers.CharField(max_length = 200 )
    new_password2 = serializers.CharField(max_length = 200 )
 
    # def validate(self, attrs):
    #     try:
    #         password_validation.validate_password(attrs.get("new_password1"))
    #         if attrs.get("new_password1") and attrs.get("new_password2") : 
    #             if attrs.get("new_password1") != attrs.get("new_password2"):
    #                 raise serializers.ValidationError(self.error_messages.get("password_mismatch"))
    #         return attrs  
    #     except:
    #         raise serializers.ValidationError(self.error_messages.get("password_requirements"))
        

    def save(self,user):
        password = self.validated_data.get("new_password1")
        user.set_password(password)
        user.save()
        return user