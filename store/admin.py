from django.contrib import admin
from .models import Category, Review, Product,Subscription



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    # Customize other admin options as needed

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'date_created')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'brand')
    # Customize other admin options as needed

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment','rating', 'product', 'createdAt')
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name')
    


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_subscribed']
    list_filter = ['is_subscribed']
    search_fields = ['email']

admin.site.register(Subscription, SubscriptionAdmin)