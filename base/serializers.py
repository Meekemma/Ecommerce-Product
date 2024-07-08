from rest_framework import serializers
from django.utils import timezone
from .models import *
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password and confirm password don't match")

        # Validate the password using Django's built-in validators
        validate_password(password)

        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('password2', None)

        # Extract the password from validated_data
        password = validated_data.pop('password')

        user = User.objects.create(**validated_data)
        # Use Django's set_password method to hash and set the password
        user.set_password(password)
        # Save the user object with the hashed password
        user.save()
        return user



    



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=255, style={'input_type': 'password'}, write_only=True)
    new_password = serializers.CharField(required=True, max_length=255, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(required=True, max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')

        # Check if the old password matches the user's current password
        if not user.check_password(old_password):
            raise serializers.ValidationError('Old password is incorrect')

        # Check that the new password and confirmation match
        if new_password != confirm_password:
            raise serializers.ValidationError("New Password and Confirm Password don't match")

        # Additional validation rules if needed
        if len(new_password) <= 6:
            raise serializers.ValidationError("Password must be at least 7 characters long")

        return attrs

    def save(self, **kwargs):
        user = self.context.get('user')
        new_password = self.validated_data['new_password']
        
        # Set the new password for the user
        user.set_password(new_password)
        user.save()
        
        return user





# Serializer for resetting user password via email
class resetPasswordEmailSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True, max_length=50, style={'input_type':'email'}, write_only=True)






class VerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


        

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'first_name', 'last_name', 'email', 'gender', 'profile_picture', 'country', 'phone_number', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated', 'email', 'user']


    def validate_phone_number(self, value):
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.country = validated_data.get('country', instance.country)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)  # Use square brackets instead of parentheses

        instance.save()
        return instance
    




class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


    




    