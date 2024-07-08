from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.category_view, name='category'),
    path('product/', views.product_view, name='product'),
    path('reviews/', views.review_view, name='review-name'),
    path('all_review/<int:product_id>/', views.product_review, name='all_review'),
    path('email-subcription/', views.email_subcription, name='email-subcription'),

]
