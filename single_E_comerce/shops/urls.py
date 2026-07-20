from django.urls import path
from . import views

urlpatterns = [
    # 1. Dashboard & Core Settings
    path('dashboard/', views.shop_owner_dashboard, name='owner_dashboard'),
    path('settings/', views.shop_settings_update, name='shop_profile_update'),
    path('billing/', views.subscription_billing, name='billing'),
    path('activity-logs/', views.activity_logs_list, name='activity_logs'),

    # 2. Shop Media (Static Path)
    path('media-all/', views.shop_media_list, name='shop_media_list'),
    path('media/add/', views.shop_media_create, name='shop_media_create'),
    path('media/delete/<int:pk>/', views.shop_media_delete, name='shop_media_delete'),

    # 3. Social Links
    path('social-links/', views.social_links_list, name='social_links_list'),
    path('social-links/add/', views.social_link_create, name='social_link_create'),
    path('social-links/delete/<int:pk>/', views.social_link_delete, name='social_link_delete'),

    # 4. Coupons
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/active/', views.active_coupons_list, name='active_coupons'),
    path('coupons/history/', views.coupon_history_list, name='coupon_history'),
    path('coupons/activity-logs/', views.coupon_activity_logs, name='coupon_activity_logs'),
    path('coupons/create/', views.coupon_create, name='coupon_create'),
    path('coupons/update/<int:pk>/', views.coupon_update, name='coupon_update'),
    path('coupons/delete/<int:pk>/', views.coupon_delete, name='coupon_delete'),

    # 5. Events (সবার নাম সামঞ্জস্য করার জন্য 'event/' কে 'events/' করা হলো)
    path('events/', views.events_list, name='events_list'),
    path('events/active/', views.active_events, name='active_events'),
    path('events/upcoming/', views.upcoming_events, name='upcoming_events'),
    path('events/history/', views.event_history, name='event_history'),
    path('events/activities/', views.activity_events_log, name='activity_events_log'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/edit/<int:id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:id>/', views.delete_event, name='delete_event'),

    # 6. Global APIs (Static Paths)
    path('api/unread-count/', views.get_unread_count_api, name='get_unread_count_api_fallback'),

    # 7. Dynamic Slug Routes (সবসময় একদম নিচে থাকবে)
    path('<slug:shop_slug>/notification/', views.shop_notifications, name='shop_notifications'),
    path('<slug:shop_slug>/api/unread-count/', views.get_unread_count_api, name='get_unread_count_api'),
]