from django.urls import path
from . import views

urlpatterns = [
    path('<slug:shop_slug>/cart/', views.cart_view, name='cart_view'),
    path('<slug:shop_slug>/cart/add-or-update/', views.add_or_update_cart, name='add_or_update_cart'),
    path('<slug:shop_slug>/remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

]










# from django.urls import path
# from . import views, views_payment

# urlpatterns = [
    
#     path('add-or-update-cart/', views.add_or_update_cart, name='add_or_update_cart'),

#     # path('cart/', views.cart, name='cart'),
#     path('checkout/', views.checkout, name='checkout'),

#     #Payment

#     # path('payment/success/<str:str_data>/', views_payment.payment_complete, name='payment_complete'),
#     # path('payment/cancel/<str:str_data>/', views_payment.payment_cancel, name='payment_cancel'),
#     # path('payment/failed/<str:str_data>/', views_payment.payment_failed, name='payment_failed'),
#     # path('payment/check/<str:str_data>/', views_payment.payment_check, name="payment_check"),
#     # path('payment/ipn/', views_payment.ssl_ipn, name='ssl_ipn'),
    
# ]