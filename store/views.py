from rest_framework import status
import json
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from store.serializers import CategorySerializer,ProductSerializer,ReviewSerializer,SubscriptionSerializer
from store.models import *
from django.contrib.auth import get_user_model
User = get_user_model()


@api_view(['GET'])
def category_view(request):
    category = Category.objects.all()
    serializer  = CategorySerializer(category, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def product_view(request):
    products = Product.objects.all()
    serializer  = ProductSerializer(products, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_view(request):
    if request.method == 'POST':
        try:
            data = request.data

            # Extract product ID from request data
            product_id = data.get('product')
            if not product_id:
                return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure the product exists
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": f"Product with id {product_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

            # Prepare review data
            review_data = {
                'rating': data.get('rating'),
                'comment': data.get('comment'),
                'product': product_id,  # Assign product ID directly
            }

            serializer = ReviewSerializer(data=review_data, context={'request': request})

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
def product_review(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": f"Product with id {product_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

    reviews = Review.objects.filter(product=product)
    serializer = ReviewSerializer(reviews, many=True)

    total_rating = Review.objects.filter(product_id=product_id).aggregate(total_rating=Sum('rating'))['total_rating']
    if total_rating is None:
        total_rating = 0
    
    response_data = {
        'product': product.name,
        'total_rating': total_rating,
        'reviews': serializer.data
    }

    return Response(response_data)



@api_view(['POST'])
def email_subcription(request):
    if request.method == 'POST':
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"detail": "Email Subcription was successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

       