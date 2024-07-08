from django.urls import path
from . import views
from .views import LogoutApi,GoogleLoginApi

from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registration/', views.registration_view, name='registration'),
    path('profile/<int:user_id>/', views.user_profile, name='profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('otp/', views.code_verification, name='otp'),
    path('resend-otp/', views.resend_otp, name='resend-otp'),

    path('google-login/', GoogleLoginApi.as_view(), name='google-login'),
    path('logout/', LogoutApi.as_view(), name='logout'),
    
]
