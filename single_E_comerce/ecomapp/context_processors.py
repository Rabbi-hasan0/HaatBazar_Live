from django.db.models import Sum
from products.models import ProductMainCategory, Wishlist
from shops.models import Shop 
from orders.models import OrderCart
from accounts.models import CustomerProfile

def global_site_settings(request):
    main_categories = ProductMainCategory.objects.filter(is_active=True).prefetch_related('sub_categories')

    wishlist_count = 0
    cart_count = 0
    cart_total_price = 0.00
    global_shop = None  
    
    first_half = ""
    second_half = ""

    # ১. প্রথমে ইউআরএল বা ওনারশিপ থেকে শপ (global_shop) নির্ধারণ করা
    current_slug = request.resolver_match.kwargs.get('shop_slug') if request.resolver_match else None
    
    if current_slug:
        global_shop = Shop.objects.filter(shop_slug=current_slug, is_active=True).first()

    if not global_shop and request.user.is_authenticated:
        if getattr(request.user, 'is_shop_owner', False):
            global_shop = Shop.objects.filter(owner__user=request.user, is_active=True).first()

    # ২. শপ নির্ধারণ হওয়ার পর কার্ট ডাটা ফিল্টার করা (নির্দিষ্ট শপের জন্য)
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        try:
            customer = CustomerProfile.objects.filter(user=request.user).first()
            if customer:
                # ডিফল্ট ফিল্টার: একটিভ এবং অর্ডার না হওয়া আইটেম
                cart_filter = {
                    'customer': customer,
                    'is_order': False,
                    'is_active': True
                }
                
                # ফিক্স: যদি নির্দিষ্ট শপ পাওয়া যায়, তবে শুধু সেই শপের প্রোডাক্ট ফিল্টার করবে
                # (নোট: আপনার OrderCart মডেলে শপের ফরেন কি যদি সরাসরি 'shop' না হয়ে 'product__shop' হয়, 
                # তবে নিচের ফিল্টারটি 'product__shop=global_shop' করে দেবেন)
                if global_shop:
                    if hasattr(OrderCart, 'shop'):
                        cart_filter['shop'] = global_shop
                    else:
                        cart_filter['product__shop'] = global_shop

                cart_items = OrderCart.objects.filter(**cart_filter)
                
                # কার্ট আইটেমের মোট সংখ্যা
                cart_count = cart_items.count()
                
                # মোট দাম হিসাব করা
                total_summary = cart_items.aggregate(total=Sum('total_amount'))
                if total_summary['total'] is not None:
                    cart_total_price = float(total_summary['total'])
                else:
                    cart_total_price = sum(float(item.product.price * item.quantity) for item in cart_items if item.product)
        except Exception as e:
            pass

    # শপের নাম দুই ভাগে ভাগ করার লজিক (লোগো ডিজাইনের জন্য)
    if global_shop:
        shop_name = global_shop.shop_name.strip()
        if ' ' in shop_name:
            first_half, second_half = shop_name.split(' ', 1)
        else:
            first_half = shop_name
            second_half = ""

    return {
        'global_categories': main_categories,
        'global_departments': main_categories,
        'global_wishlist_count': wishlist_count,
        'global_cart_count': cart_count,        
        'global_cart_total': cart_total_price, 
        'global_shop': global_shop,  
        'shop_first_half': first_half,   
        'shop_second_half': second_half, 
    }