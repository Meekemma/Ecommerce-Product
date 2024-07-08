from django.shortcuts import render,redirect
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from .serializers import RegisterUserSerializer,ChangePasswordSerializer,UserProfileSerializer,AuthSerializer
from .services import get_user_data
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .utils import send_code_to_user,verify_otp
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import login,logout
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from urllib.parse import urlencode
from rest_framework_simplejwt.tokens import RefreshToken


from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *

# Create your views here.



# Custom serializer for obtaining JWT token with additional claims
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['email'] = user.email
        token['is_verified'] = user.is_verified
       
        

        return token
    
# validate method is overridden to add extra responses to the data returned by the parent class's validate method.
    def validate(self, attrs):
        # call validates the provided attributes using the parent class's validate method and returns the validated data.
        data = super().validate(attrs)

        # Add extra responses
        # Adds the user id to the response
        data.update({'user_id': self.user.id})
        data.update({'email': self.user.email})
        data.update({'is_verified': self.user.is_verified})
       

        return data

    
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class =MyTokenObtainPairSerializer 



@csrf_exempt
@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            send_code_to_user(user.email)
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response({"error": "Failed to register user", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'PUT':
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()  
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to change password", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])
def user_profile(request, user_id):
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'User profile updated successfully'}, status=status.HTTP_200_OK)

    return Response({"error": "Failed to update user profile"}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def code_verification(request):
    if request.method == 'POST':
        otp_code = request.data.get('code') # Extract the OTP code from the request data
        if not otp_code:
            # If OTP code is not provided, return a bad request response
            return Response({'message': 'Passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to find a OneTimePassword object with the provided OTP code
            user_code_obj = OneTimePassword.objects.get(code=otp_code)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True  # If the user is not verified, mark them as verified and save
                user.save()
                return Response({'message': 'Account email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Code is invalid, user already verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        except OneTimePassword.DoesNotExist:
            return Response({'message': 'Invalid passcode'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def resend_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    send_result = send_code_to_user(user.email)
    if "Failed" in send_result:
        return Response({'error': send_result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Assuming the send_code_to_user function returns a success message on success
    if send_result == "OTP sent successfully":
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    else:
        # Handling any other unexpected response from the utility function
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    







class GoogleLoginApi(APIView):
    def get(self, request, *args, **kwargs):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        
        validated_data = auth_serializer.validated_data
        user_data = get_user_data(validated_data)
        
        user = User.objects.get(email=user_data['email'])
        login(request, user)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        

        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'id':user_data['id'],
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'is_verified': user.is_verified
        }
        # Print access and refresh tokens
        
        

        if settings.BASE_APP_URL:
            # Add response data to query parameters for the redirect URL
            query_params = urlencode(response_data)
            redirect_url = f"{settings.BASE_APP_URL}?{query_params}"
            return redirect(redirect_url)
        
        return Response(response_data, status=status.HTTP_200_OK)


class LogoutApi(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponse('200')