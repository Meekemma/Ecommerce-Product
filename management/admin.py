from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem, Wishlist,  Coupon



@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'city', 'state', 'zipcode', 'country')
    search_fields = ('user', 'address', 'city', 'state', 'zipcode', 'country')




@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'ordered_date', 'status')
    search_fields = ('id', 'status')
    list_filter = ('status', 'ordered_date')



@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity','date_added')
    search_fields = ('order__id', 'product__name')




class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'display_products', 'added_at')

    def display_products(self, obj):
        return ", ".join([product.name for product in obj.products.all()])

    display_products.short_description = 'Product'

admin.site.register(Wishlist, WishlistAdmin)





class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'discount_percentage', 'expiration_date', 'is_active', 'minimum_order_value')
    search_fields = ('code',)
    list_filter = ('expiration_date',)

admin.site.register(Coupon, CouponAdmin)
