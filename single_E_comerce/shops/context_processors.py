from .models import Shop, ShopNotification

def shop_global_notifications(request):
    # ইউজার লগইন না থাকলে খালি ডিকশনারি রিটার্ন করবে
    if not request.user.is_authenticated:
        return {}
    
    # ইউআরএল থেকে শপের স্লাগ খুঁজে বের করার চেষ্টা করা (আপনার URL প্যাটার্ন অনুযায়ী)
    # ধরি আপনার ড্যাশবোর্ডের ইউআরএল-এ 'shop_slug' ভ্যারিয়েবলটি আছে
    resolver_match = request.resolver_match
    if resolver_match and 'shop_slug' in resolver_match.kwargs:
        shop_slug = resolver_match.kwargs['shop_slug']
        try:
            shop = Shop.objects.get(shop_slug=shop_slug, owner__user=request.user)
            unread_count = ShopNotification.objects.filter(shop=shop, is_read=False).count()
            return {
                'global_unread_count': unread_count,
                'current_shop': shop # শপ অবজেক্টটিও গ্লোবালি পেয়ে যাবেন
            }
        except Shop.DoesNotExist:
            pass
            
    return {}