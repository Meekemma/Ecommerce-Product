from rest_framework import serializers
from django.utils import timezone
from store.models import *
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model
User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields = ('id','name')
        read_only_fields=('id','user')



class  ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model= Product
        fields = ('id','name','description','price','image','category','brand','date_created')
        read_only_fields=('id','user','date_created')



class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = Review
        fields = ('id', 'user', 'rating', 'comment', 'product', 'createdAt')
        read_only_fields = ('id', 'user', 'createdAt')


    def validate_rating(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError('Rating has to be between 0 and 5')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        review = Review.objects.create(user=user, **validated_data)
        return review




class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'email', 'subscribed_at', 'is_subscribed']
        read_only_fields = ['id', 'subscribed_at']

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid email format")

        subscribed = Subscription.objects.filter(email=value).first()
        if subscribed:
            raise serializers.ValidationError("Email already registered, please use a different email")

        return value 

    def validate_is_subscribed(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Subscription status must be a boolean value")
        return value

    def create(self, validated_data):
        return Subscription.objects.create( **validated_data)
