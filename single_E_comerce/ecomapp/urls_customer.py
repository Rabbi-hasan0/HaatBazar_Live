from django.urls import path
from . import views_customer 

urlpatterns = [
    path('<slug:shop_slug>/coming-soon/', views_customer.page_coming_soon, name='page_coming_soon'),
    
    # শপের মেইন ড্যাশবোর্ড/হোম
    path('<slug:shop_slug>/', views_customer.shop_home_page, name='user_dashboard'),
    path('<slug:shop_slug>/contact/', views_customer.contact_us, name='contact_us'),
    path('<slug:shop_slug>/about/', views_customer.customer_about_us, name='customer_about_us'),
    path('<slug:shop_slug>/media/', views_customer.shop_profile_media, name='shop_profile_media'),
    
    # অফার এবং ইভেন্টস
    path('<slug:shop_slug>/offers/', views_customer.customer_events_list, name='customer_events_list'),
    path('<slug:shop_slug>/offers/<slug:slug>/', views_customer.customer_event_details, name='customer_event_details'),
    
    # ভাউচার ও কুপন
    path('<slug:shop_slug>/user/vouchers/', views_customer.customer_coupons_list, name='customer_coupons_list'),
    path('<slug:shop_slug>/user/vouchers/<str:code>/', views_customer.customer_coupon_details, name='customer_coupon_details'),
    
    # রিভিউ এবং উইশলিস্ট
    path('<slug:shop_slug>/wishlist/<str:username>/', views_customer.view_wishlist, name='wishlist_list'),
    path('<slug:shop_slug>/wishlist/toggle/<slug:slug>/', views_customer.toggle_wishlist, name='toggle_wishlist'),
    path('<slug:shop_slug>/wishlist/remove/<slug:slug>/', views_customer.remove_from_wishlist, name='remove_from_wishlist'),
    
    # প্রোডাক্ট এবং ক্যাটাগরি
    path('<slug:shop_slug>/products/', views_customer.shop_products, name='shop_products'),
    path('<slug:shop_slug>/discount/', views_customer.discount_products, name='discount_products'),
    path('<slug:shop_slug>/product/<slug:slug>/', views_customer.product_detail, name='product_detail'),
    path('<slug:shop_slug>/products/<slug:slug>/', views_customer.sub_category_products, name='sub_category_products'),
    path('<slug:shop_slug>/product/review/add/<slug:slug>/', views_customer.add_product_review, name='add_product_review'),
]