from django.urls import path
from accounts import views

urlpatterns = [
    # Auth Routes
    path('merchant/register/', views.merchant_register, name='merchant_register'),
    path('merchant/login/', views.merchant_login, name='merchant_login'),
    path('merchant/logout/', views.merchant_logout, name='merchant_logout'),
    path('shop/verify-otp/', views.verify_otp_shop_account, name='verify_otp_shop_account'),
    path('shop/request-otp/', views.request_otp_for_shop, name='request_shop_otp'),

    # Customer Routes
    path('login/', views.customer_login, name='customer_login'),
    path('register/', views.customer_register, name='customer_register'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('verify-otp/', views.verify_otp_customer_account, name='verify_otp_customer_account'),
    path('request-otp/', views.request_otp_for_customer, name='request_otp_for_customer'),

    # Forgot Password
    path('merchant/forgot-password/', views.merchant_forgot_password, name='merchant_forgot_password'),
    path('merchant/reset-password/', views.merchant_reset_password, name='merchant_reset_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # Owner profile setting 
    path('account-setting/', views.merchant_account_setting, name='merchant_account_setting'),
    path('profile_pic/edit/', views.edit_merchant_profile_pic, name='edit_merchant_profile_pic'),
    path('profile/edit/', views.edit_merchant_profile, name='edit_merchant_profile'),
    
    # Customer profile setting
    path('customer/settings/', views.customer_account_setting, name='customer_account_setting'),
    path('customer/settings/edit-pic/', views.edit_customer_profile_pic, name='edit_customer_profile_pic'),
    path('customer/settings/edit-profile/', views.edit_customer_profile, name='edit_customer_profile'),
]