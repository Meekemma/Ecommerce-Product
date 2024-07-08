from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from management.serializers import OrderSerializer,OrderItemSerializer,ShippingAddressSerializer,WishlistSerializer
from management.models import *
from django.contrib.auth import get_user_model
User = get_user_model()


@api_view(['POST'])
def create_order(request):

    # Deserialize the request data using OrderSerializer
    serializer = OrderSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def order_item(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    order_items = OrderItem.objects.filter(order=order)
    serializer = OrderItemSerializer(order_items, many=True)
    return Response(serializer.data)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_shipping_address(request):
    if request.method == 'GET':
        addresses = ShippingAddress.objects.all()
        serializer = ShippingAddressSerializer(addresses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ShippingAddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_shipping_address(request, pk):
    try:
        shipping_address = ShippingAddress.objects.get(pk=pk)
    except ShippingAddress.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = ShippingAddressSerializer(shipping_address, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        serializer = ShippingAddressSerializer(shipping_address, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def wishlists(request):
    if request.method == 'GET':
        wishlists = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlists, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = WishlistSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_wishlist(request, pk):
    try:
        wish_list = Wishlist.objects.get(id=pk)
    except Wishlist.DoesNotExist:
        return Response (status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        serializer = WishlistSerializer(wish_list, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        serializer = WishlistSerializer(wish_list, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        wish_list.delete()
        return Response (status=status.HTTP_200_OK)
