from django.urls import path
from .views import home_page_view

urlpatterns = [
    path('all-shops/', home_page_view, name='haatbazar_home'),
]