
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import debug_toolbar
from django.conf.urls.static import static
from django.shortcuts import render

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


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# def custom_404_view(request, exception=None):
#     return render(request, 'errorrs/404.html', status=404)

# handler404 = custom_404_view