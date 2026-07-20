from django.urls import path
from . import views

urlpatterns = [
    # --- main category --- 
    path('main-category/list/', views.main_category_list, name='main_category_list'),
    path('main-category/add', views.main_category_add, name='main_category_add'),
    path('main-category/edit/<int:pk>/', views.main_category_edit, name='main_category_edit'),
    path('main-category/delete/<int:pk>/', views.main_category_delete, name='main_category_delete'),
    # --- sub category ---
    path('sub-category/list/', views.sub_category_list, name='sub_category_list'),
    path('sub-category/add', views.sub_category_add, name='sub_category_add'),
    path('sub-category/edit/<int:pk>/', views.sub_category_edit, name='sub_category_edit'),
    path('sub-category/delete/<int:pk>/', views.sub_category_delete, name='sub_category_delete'),
    # --- product category --- 
    path('product/list/', views.product_list, name='product_list'),
    path('product/add/', views.product_add, name='product_add'),
    path('product/edit/<int:id>/', views.product_edit, name='product_edit'),
    path('product/delete/<int:id>/', views.product_delete, name='product_delete'),
    path('product/bulk-delete/', views.product_bulk_delete, name='product_bulk_delete'),
    
    #Activity log 
    path('products/activity-log/', views.activity_log_list, name='activity_log_list'),
    
    # Product reviews
    # path('product/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
]