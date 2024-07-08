from django.db import models
from store.models import Product
from django.utils import timezone
from functools import cached_property 
from django.contrib.auth import get_user_model
User = get_user_model()

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.country}"

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    

    def __str__(self):
        return f"Order {self.id} - {self.user}"
    
   
    @property
    def get_cart_items(self):
        """
        Get the total quantity of items in the order.
        """
        order_items = self.orderitem_set.all()
        total_quantity = sum([item.quantity for item in order_items])
        return total_quantity
    
    @property
    def get_cart_total(self):
        """
        Get the total cost of items in the order.
        """
        order_items = self.orderitem_set.all()
        cart_total= sum([item.get_item_total for item in order_items])
        return cart_total



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order for {self.order.user}"
    

    @property
    def get_item_total(self):
        item_total = self.product.price * self.quantity
        return item_total
    



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Default Wishlist")
    products = models.ManyToManyField(Product, related_name='wishlists')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    expiration_date = models.DateTimeField()
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active  = models.BooleanField(default=False,editable=False)

    def __str__(self):
        return self.code
    

    @cached_property
    def is_valid(self):
        if self.expiration_date < timezone.now():
            return False
        if self.used:
            return False
        return True
    


    @cached_property
    def apply_discount(self,  total_price):
        if not self.is_valid():
            return  total_price
        if self.minimum_order_value and  total_price < self.minimum_order_value:
            return  total_price
        if self.discount_amount:
            return max( total_price - self.discount_amount, 0)
        if self.discount_percentage:
            discount =  total_price * (self.discount_percentage / 100)
            return max( total_price - discount, 0)
        return  total_price
    

    @cached_property
    def mark_is_active (self):
        self.is_active  = True
        self.save()
    
