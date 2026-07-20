from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.order_list, name='order_list'),
    path('<int:order_id>/details/', views.order_detail, name='order_detail'),
    path('<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('activity/', views.order_activity_log, name='order_activity_log'),
    path('bulk-delete/', views.order_bulk_delete, name='order_bulk_delete'),
]