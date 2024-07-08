from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from urllib.parse import urlencode
from typing import Dict, Any
import requests
from django.contrib.auth import get_user_model

User = get_user_model()


# URLs for Google OAuth2 token exchange and user info
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'




## Function to exchange authorization code for access and refresh tokens
def google_get_access_and_refresh_tokens(code: str, redirect_uri: str) -> Dict[str, str]:
    # Data required to get access token
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'access_type': 'offline',
        'prompt': 'consent'
    }

    # Request to get access token
    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    if not response.ok:
        raise ValidationError('Could not get tokens from Google.')
    tokens = response.json()
    return tokens


# Function to get user information from Google using the access token
def google_get_user_info(access_token: str) -> Dict[str, Any]:
    response = requests.get(GOOGLE_USER_INFO_URL, params={'access_token': access_token})
    if not response.ok:
        raise ValidationError('Could not get user info from Google.')
    return response.json()


# Function to handle user data retrieval and user creation
def get_user_data(validated_data: Dict[str, str]) -> Dict[str, str]:
    domain = settings.BASE_API_URL
    redirect_uri = f'{domain}/google-login/'

    # Extract code and error from the validated data
    code = validated_data.get('code')
    error = validated_data.get('error')

    # If there is an error or no code, redirect to login with error parameters
    if error or not code:
        params = urlencode({'error': error})
        raise ValidationError('Error or no code provided.')

    # Exchange code for access token
    tokens = google_get_access_and_refresh_tokens(code=code, redirect_uri=redirect_uri)
    access_token = tokens['access_token']
    refresh_token = tokens.get('refresh_token')

    # Get user info using the access token
    user_data = google_get_user_info(access_token=access_token)

    # Creates user in database if it's their first login
    user, created = User.objects.get_or_create(
        email=user_data['email'],
        defaults={
            'first_name': user_data.get('given_name'),
            'last_name': user_data.get('family_name'),
            'profile_picture': user_data.get('picture')
        }
    )
    if created:
        user.auth_provider = 'google'
        user.is_verified = True
        user.save()

    # Prepare user profile data
    profile_data = {
        'id': user.id, 
        'email': user_data['email'],
        'first_name': user_data.get('given_name'),
        'last_name': user_data.get('family_name'),
        'profile_picture': user_data.get('picture'),
    }

    return profile_data