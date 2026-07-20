from django.urls import path
from admin_management import views

urlpatterns = [
    # Services 
    path('support/services/', views.support_services, name='haatbazar_service'),
    # Shop/Profile Settings
    # path('profile/', views.shop_profile, name='shop_profile'),
    # path('settings/payment-gateway/', views.payment_settings, name='payment_settings'),
    
    # # Staff Management (Role Based)
    # path('staff/list/', views.staff_list, name='staff_list'),
    # path('staff/roles/', views.role_management, name='role_management'),
    
]