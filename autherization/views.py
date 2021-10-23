from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import LocationSerializer, RegisterSerializer,check,LoginSerializer
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate
from django.contrib.auth import login,logout
from django.urls import reverse
from .utils import Util
from rest_framework.authtoken.models import Token
from .models import Location
import requests

# Create your views here.
class LoginView(generics.GenericAPIView):
    """
    TODO:
    Implement login functionality, taking username and password
    as input, and returning the Token.
    """
    serializer_class = LoginSerializer

    def post(self,request):
        email = request.data.get("email")
        password = request.data.get("password")
        if email is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                        status=400)  
        user = authenticate(username=email, password=password)
        if not user or user.is_active==False:
            return Response({'error': 'User not authorized!'},
                        status=status.HTTP_401_UNAUTHORIZED)   
        login(request,user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class LogoutView(generics.GenericAPIView):
    """
    TODO:
    Implement logout functionality, logout the user.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LoginSerializer

    def get(self,request):
        request.user.auth_token.delete()
        logout(request)

        return Response(status=status.HTTP_200_OK)    

def create_auth_token(user):
    """
    Returns the token required for authentication for a user.
    """
    token, _ = Token.objects.get_or_create(user=user)
    return token

class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class=RegisterSerializer
    
    def post(self,request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=check(request.data)
            if user is None:
                user=serializer.save()
                create_auth_token(user=user)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(request=request).domain
                relativeLink = reverse('activate-account', kwargs={'uidb64': uidb64, 'token': token})
                absurl = 'http://' + current_site + relativeLink
                email_body = 'Hello '+user.username+',\nUse this link to activate your account: \n'+absurl
                data = {'email_body': email_body, 'to_mail': user.email, 'email_subject': 'Verify your email'}
                Util.send_email(data)
                return Response({'success': 'Verification link has been sent by email!'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User with same credentials already exists!'},status=status.HTTP_226_IM_USED)
        else:    
            # print(serializer.errors)
            return Response({'error': serializer.errors},status=status.HTTP_409_CONFLICT)

class ActivateAccountView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class=RegisterSerializer
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Invalid token! Try again.'}, status=status.HTTP_401_UNAUTHORIZED)
            user.is_active=True
            user.save()
            return Response({'message': 'Your account is verified.'}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Invalid token! Try again.'}, status=status.HTTP_401_UNAUTHORIZED)

class AlertView(generics.GenericAPIView):
    queryset=Location.objects.all()
    serializer_class=LocationSerializer
    def get(self, request):
        data=Location.objects.get(user=request.user)
        if(data==None):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        content={
            'lat':data.lat,
            'long':data.long,
            'city':data.city
        }
        return Response(content, status=status.HTTP_200_OK)

    def post(self,request):
        data=Location.objects.get(user=request.user)
        if(data is not None):
            if(data.rainfallalert==False): create_email(data)
            return Response({'success': 'Subscribed to email alerts!'}, status=status.HTTP_200_OK)
        serializer=LocationSerializer(data=request.data)
        if serializer.is_valid():
            data=serializer.save()
            data.user=request.user
            data.save()
            return Response({'success': 'Subscribed to email alerts!'}, status=status.HTTP_200_OK)
        else:  
            return Response({'error': serializer.errors},status=status.HTTP_409_CONFLICT)

    def delete(self,request):
        data=Location.objects.get(user=request.user)
        delete_email(data)
        return Response(status=status.HTTP_200_OK)

def create_email(data):
    url="https://script.google.com/macros/s/AKfycbx_Oj8QTm9v-vv3CdGEqS24lIdv8P2J4VhVzVLg6rSSNId3lslyK87Yo2ZZ7zWgl8Pdzw/exec"
    user=data.user
    body={
        "Name":user.first_name,
        "Email":user.email,
        "Lat":data.lat,
        "Long":data.long
    }
    req = requests.post(url,params=body)

def delete_email(data):
    url="https://script.google.com/macros/s/AKfycbx_Oj8QTm9v-vv3CdGEqS24lIdv8P2J4VhVzVLg6rSSNId3lslyK87Yo2ZZ7zWgl8Pdzw/exec"
    user=data.user
    body={
        "name":user.first_name,
    }
    req = requests.get(url,params=body)
    data.rainfallalert=False
    data.save()