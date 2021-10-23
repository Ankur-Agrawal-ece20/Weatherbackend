from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from .models import Location

def check(data):
    return authenticate(username=data['username'], password=data['password'])

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    class Meta:
        model = User
        fields = ('email', 'password')

class RegisterSerializer(serializers.Serializer):
    # TODO: Implement register functionality
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(
            required=True
            )
    last_name = serializers.CharField(
            required=True
            )
    class Meta:
        model = User
        fields = '__all__'
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.is_active=False
        user.first_name=validated_data['first_name']
        user.last_name=validated_data['last_name']
        user.save()
        return user

class LocationSerializer(serializers.Serializer):
    lat = serializers.CharField()
    long = serializers.CharField()
    city = serializers.CharField()
    class Meta:
        model = Location
        fields = ('user','lat','long','city')
    def create(self, validated_data):
        userdata = Location.objects.create(
            lat=validated_data['lat'],
            long=validated_data['long'],
            city=validated_data['city']
        )
        userdata.save()
        return userdata