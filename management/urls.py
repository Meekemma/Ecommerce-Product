from django.urls import path
from . import views

urlpatterns = [
    path('order-items/', views.create_order, name='orderitem-list-create'),
    path('create_shipping_address/', views.create_shipping_address, name='create_shipping_address'),
    path('update_shipping_address/<int:pk>/', views.update_shipping_address, name='update_shipping_address'),
    path('order_item/<int:order_id>/', views.order_item, name='order_item'),
    path('wishlist/', views.wishlists, name='wishlist'),
    path('update_wishlist/<int:pk>/', views.update_wishlist, name='wishlist'),
]
