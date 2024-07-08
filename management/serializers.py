from rest_framework import serializers
from management.models import Product, Order, OrderItem,ShippingAddress, Wishlist
from django.contrib.auth import get_user_model



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price')
        read_only_fields = ('id',)



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'date_added', 'item_total')
        read_only_fields = ('id', 'date_added')

    def get_item_total(self, obj):
        return obj.get_item_total



class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='orderitem_set')
    total_price = serializers.SerializerMethodField()
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'ordered_date', 'status', 'order_items', 'cart_items')
        read_only_fields = ('id', 'user', 'total_price', 'ordered_date')

    def get_total_price(self, obj):
        return obj.get_cart_total

    def get_cart_items(self, obj):
        return obj.get_cart_items

    def create(self, validated_data):
        user = self.context['request'].user
        order_items_data = validated_data.pop('orderitem_set')  # Use 'orderitem_set' to match related_name
        order,created = Order.objects.get_or_create(user=user, **validated_data)

        for item_data in order_items_data:
            OrderItem.objects.get_or_create(order=order, **item_data)

        # Update the total_price after creating all order items
        

        order.total_price = order.get_cart_total
        order.save()

        return order
    

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ('id','user','address','city','state','zipcode','country')
        read_only_fields = ('id','user',)

    def create(self, validated_data):
        user = self.context['request'].user
        shipping_address, created = ShippingAddress.objects.get_or_create(user=user, **validated_data)
        return shipping_address
    
    def update(self, instance, validated_data):
        instance.address = validated_data.get('address',  instance.address)
        instance.city = validated_data.get('city',  instance.city)
        instance.state = validated_data.get('state',  instance.state)
        instance.zipcode = validated_data.get('zipcode',  instance.zipcode)
        instance.country = validated_data.get('country',  instance.country)

        instance.save()
        return instance





class WishlistSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True, required=False)

    class Meta:
        model = Wishlist
        fields = ('id', 'user', 'name', 'products', 'added_at')
        read_only_fields = ('user', 'id', 'added_at')

    def create(self, validated_data):
        products_data = validated_data.pop('products', [])
        wishlist,created = Wishlist.objects.get_or_create(user=self.context['request'].user, **validated_data)
        wishlist.products.set(products_data)
        return wishlist

    def update(self, instance, validated_data):
        products_data = validated_data.pop('products', None)
        instance.name = validated_data.get('name', instance.name)

        if products_data is not None:
            instance.products.set(products_data)
        
        instance.save()
        return instance
