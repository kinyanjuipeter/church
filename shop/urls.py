from django.urls import path
from . import views

app_name = 'shop_cart'  # Changed to make namespace unique

from .views import product_list_redirect, product_detail_redirect, cart_detail_redirect

urlpatterns = [
    # Legacy redirects
    path('shop/', product_list_redirect),
    path('shop/<slug:category_slug>/', product_list_redirect),
    path('shop/<int:id>/<slug:slug>/', product_detail_redirect),
    path('shop/cart/', cart_detail_redirect),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, 
         name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail,
         name='product_detail'),
    path('cart/guest-checkout/', views.guest_checkout, name='guest_checkout'),
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('cart/create-order/', views.create_order, name='create_order'),
]
