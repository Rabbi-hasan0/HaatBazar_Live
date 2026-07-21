from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('haatbazar/accounts/', include('accounts.urls')),
    path('haatbazar/', include('admin_management.urls')),
    path('haatbazar/', include('haatbazar.urls')),
    path('haatbazar/', include('ecomapp.urls')),
    path('haatbazar/', include('ecomapp.urls_customer')),
    path('haatbazar/shops/', include('shops.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]


urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]