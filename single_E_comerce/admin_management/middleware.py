from django.shortcuts import get_object_or_404
from django.http import Http404
from shops.models import Shop

class ShopMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        host = request.get_host().split('.')
        
        if len(host) > 2:
            subdomain = host[0]
            try:
                request.shop = Shop.objects.get(shop_slug=subdomain, is_active=True)
            except Shop.DoesNotExist:
                raise Http404("Shop not found")
        else:
            request.shop = None

        return self.get_response(request)