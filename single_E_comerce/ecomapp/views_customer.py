from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from ecomapp.models import *
from django.utils import timezone
from django.db.models import Avg, Count, Prefetch, F
from django.contrib.auth.decorators import login_required
from shops.models import Events, Shop, Coupon
from products.models import ProductSubCategory, Product, ProductMainCategory, ProductReview, Wishlist
from accounts.models import ShopOwnerProfile
from django.db.models import Q
from orders.models import Order
from shops.models import ShopMedia, ShopSocialMedia, ShopNotification, Shop
from admin_management.utils import send_email

def page_coming_soon(request, shop_slug):
    return render(request, 'errorrs/coming_soon.html')

def shop_home_page(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    now = timezone.now()
    
    active_events = Events.objects.filter(
        shop=shop,
        status='active', 
        start_time__lte=now, 
        end_time__gte=now
    ).order_by('-priority', '-created_at')
    
    main_categories = ProductMainCategory.objects.filter(
        is_active=True,
        sub_categories__products__shop=shop
    ).distinct()
    
    categories = ProductSubCategory.objects.filter(
        is_active=True,
        products__shop=shop
    ).distinct()
    
    featured_products = Product.objects.filter(
        shop=shop,
        is_featured=True, 
        is_active=True
    ).order_by('-created_at')[:10]
    
    most_selling_products = Product.objects.filter(
        shop=shop,
        is_active=True
    ).annotate(
        total_loves=Count('wishlisted_by')
    ).order_by('-total_loves')[:10]
        
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(
            user=request.user,
            shop=shop
        ).values_list('product_id', flat=True)
        
    context = {
        'slider_events': active_events,
        'main_categories': main_categories,
        'categories': categories,
        'featured_products': featured_products,
        'most_selling_products': most_selling_products,
        'user_wishlist_ids': user_wishlist_ids,
        'shop': shop,
    }
    return render(request, 'customer_site/dashboard/index.html', context)

def shop_products(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    
    Shop.objects.filter(id=shop.id).update(total_views=F('total_views') + 1)
    
    shop_products = Product.objects.filter(shop=shop, is_active=True).order_by('-id')
    
    search_query = request.GET.get('product_search')
    if search_query:
        search_query = search_query.strip()
        shop_products = shop_products.filter(
            Q(product_name__icontains=search_query) |
            Q(main_category__main_cat_name__icontains=search_query) |
            Q(sub_category__sub_cat_name__icontains=search_query)
        ).distinct()
    
    sub_cat_prefetch = ProductSubCategory.objects.filter(
        is_active=True,
        products__in=shop_products
    ).prefetch_related(
        Prefetch('products', queryset=shop_products, to_attr='shop_assigned_products')
    ).distinct()
    
    categories = ProductMainCategory.objects.filter(
        is_active=True,
        sub_categories__in=sub_cat_prefetch
    ).prefetch_related(
        Prefetch('sub_categories', queryset=sub_cat_prefetch)
    ).distinct()
    
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        
    context = {
        'shop': shop,
        'categories': categories,
        'user_wishlist_ids': user_wishlist_ids,
    }
    return render(request, 'customer_site/shop_products.html', context)

def sub_category_products(request, shop_slug, slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    sub_category = get_object_or_404(ProductSubCategory, sub_cat_slug=slug, is_active=True)
    
    products = Product.objects.filter(shop=shop, sub_category=sub_category, is_active=True).exclude(product_slug="").distinct()
    
    other_sub_categories = ProductSubCategory.objects.filter(
        is_active=True,
        products__shop=shop
    ).exclude(id=sub_category.id).distinct()[:10]
    
    main_categories = ProductMainCategory.objects.filter(
        is_active=True,
        sub_categories__products__shop=shop
    ).distinct()
    
    context = {
        'shop': shop,
        'sub_category': sub_category,
        'products': products,
        'other_sub_categories': other_sub_categories,
        'main_categories': main_categories,
    }
    return render(request, 'customer_site/products.html', context)

def discount_products(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    discount_ed_products = Product.objects.filter(
        shop=shop,
        is_active=True,
        discount_price__gt=0,
    ).order_by('-id')
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    context = {
        'shop': shop,
        'products': discount_ed_products,
        'user_wishlist_ids': user_wishlist_ids,
    }
    return render(request, 'customer_site/discount_products.html', context)

def product_detail(request, shop_slug, slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    product = get_object_or_404(Product, shop=shop, product_slug=slug, is_active=True)
    
    reviews = ProductReview.objects.filter(product=product, is_active=True).order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    average_rating = round(average_rating, 1) if average_rating else 5.0  
    
    wishlist_count = Wishlist.objects.filter(product=product).count()
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        
    related_products = Product.objects.filter(
        shop=shop,
        main_category=product.main_category, 
        is_active=True
    ).exclude(id=product.id).order_by('-id')[:4]
    
    main_categories = ProductMainCategory.objects.filter(
        is_active=True,
        sub_categories__products__shop=shop
    ).distinct()
    
    context = {
        'shop': shop,
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'average_rating': average_rating,
        'wishlist_count': wishlist_count,
        'main_categories': main_categories,
        'is_in_wishlist': is_in_wishlist,
    }
    return render(request, 'customer_site/product_detail.html', context)

@login_required
def add_product_review(request, shop_slug, slug):
    if request.method == "POST":
        shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
        product = get_object_or_404(Product, shop=shop, product_slug=slug, is_active=True)
        
        rating_val = request.POST.get('rating')
        review_text_val = request.POST.get('review_text')
        
        if not rating_val or not review_text_val:
            messages.error(request, "Please select a star rating and write a comment.")
            return redirect('product_detail', shop_slug=shop_slug, slug=product.product_slug)
            
        try:
            shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=shop.owner.user)

            ProductReview.objects.create(
                product=product,
                user=request.user,
                shop=shop,
                rating=int(rating_val),
                comment=review_text_val,
                is_active=True,
                created_by=shop_owner_profile,
            )
            messages.success(request, "Thank you! Your review has been submitted successfully.")
            
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            
        return redirect('product_detail', shop_slug=shop_slug, slug=product.product_slug)

    return redirect('product_detail', shop_slug=shop_slug, slug=slug)

@login_required
def toggle_wishlist(request, shop_slug, slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    product = get_object_or_404(Product, shop=shop, product_slug=slug, is_active=True)
    
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        Wishlist.objects.create(user=request.user, product=product, shop=shop)
    return HttpResponse(status=204)

@login_required
def remove_from_wishlist(request, shop_slug, slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    product = get_object_or_404(Product, shop=shop, product_slug=slug, is_active=True)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect(request.META.get('HTTP_REFERER', 'home_page'))

@login_required
def view_wishlist(request, shop_slug, username):
    if request.user.username != username:
        messages.error(request, "You are not authorized to view this wishlist.")
        previous_page = request.META.get('HTTP_REFERER')
        if previous_page:
            return redirect(previous_page)
        return redirect('customer_login')
    
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    wishlist_items = Wishlist.objects.filter(user=request.user, shop=shop).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
        'shop': shop,
    }
    return render(request, 'customer_site/wishlist.html', context)

def customer_events_list(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    now = timezone.now()
    
    running_events = Events.objects.filter(
        shop=shop,
        status='active',
        start_time__lte=now,
        end_time__gte=now
    ).prefetch_related('product').order_by('-priority', '-created_at')
    
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user, shop=shop).values_list('product_id', flat=True)
        
    context = {
        'shop': shop,
        'events': running_events,
        'user_wishlist_ids': user_wishlist_ids,
    }
    return render(request, 'customer_site/offers_list.html', context)

def customer_event_details(request, shop_slug, slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    now = timezone.now()
    
    event = get_object_or_404(
        Events.objects.prefetch_related('product'), 
        shop=shop,
        slug=slug, 
        status='active',
        start_time__lte=now,
        end_time__gte=now
    )
    
    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = Wishlist.objects.filter(user=request.user, shop=shop).values_list('product_id', flat=True)
        
    context = {
        'event': event,
        'shop': shop,
        'user_wishlist_ids': user_wishlist_ids,
    }
    return render(request, 'customer_site/event_details.html', context)

def customer_coupons_list(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    now = timezone.now()
    
    base_query = Coupon.objects.filter(
        shop=shop,
        is_active=True,
        valid_from__lte=now,
        valid_to__gte=now
    ).distinct() 
    
    if request.user.is_authenticated:
        coupons = base_query.filter(
            Q(user=request.user) | Q(user__isnull=True)
        ).order_by('-id')
    else:
        coupons = base_query.filter(user__isnull=True).order_by('-id')
        
    context = {
        'coupons': coupons,
        'shop': shop,   
    }
    return render(request, 'customer_site/coupons_list.html', context)

def customer_coupon_details(request, shop_slug, code):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    now = timezone.now()
    
    if request.user.is_authenticated:
        coupon = get_object_or_404(
            Coupon,
            Q(user=request.user) | Q(user__isnull=True),
            shop=shop,
            code__iexact=code,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now
        )
    else:
        coupon = get_object_or_404(
            Coupon,
            shop=shop,
            code__iexact=code,
            user__isnull=True,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now
        )
        
    context = {
        'coupon': coupon,
        'shop': shop,
    }
    return render(request, 'customer_site/coupon_details.html', context)

def customer_about_us(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    
    owner_total_shops = 0
    if shop.owner:
        owner_total_shops = Shop.objects.filter(owner=shop.owner).count()
    
    total_wishes = Wishlist.objects.filter(shop=shop).count()
    
    total_products = Product.objects.filter(shop=shop, is_active=True).count()
    
    total_orders = Order.objects.filter(shop=shop).count()

    context = {
        'about_shop': shop,
        'owner_total_shops': owner_total_shops,
        'total_wishes': total_wishes,
        'total_orders': total_orders,
        'total_views': shop.total_views,  
        'total_products': total_products,
    }
    return render(request, 'customer_site/customer_about_us.html', context)

def shop_profile_media(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    Shop.objects.filter(id=shop.id).update(total_views=F('total_views') + 1)
    
    social_links = ShopSocialMedia.objects.filter(shop=shop, is_active=True)
    shop_banners = ShopMedia.objects.filter(shop=shop, media_type='Banner').order_by('-created_at')
    shop_certificates = ShopMedia.objects.filter(shop=shop, media_type='Certificate').order_by('-created_at')
    shop_gallery = ShopMedia.objects.filter(shop=shop, media_type='Gallery').order_by('-created_at')
    total_products = Product.objects.filter(shop=shop, is_active=True).count()

    context = {
        'shop': shop,
        'social_links': social_links,
        'shop_banners': shop_banners,
        'shop_certificates': shop_certificates,
        'shop_gallery': shop_gallery,
        'total_products': total_products,
    }
    return render(request, 'customer_site/shop_profile_media.html', context)

def contact_us(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, is_active=True)
    
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_body = request.POST.get('message')
        
        email_context = {
            'sender_name': name,
            'sender_email': email,
            'message_subject': subject,
            'message_body': message_body,
            'shop_name': shop.shop_name,
        }
        owner_email = shop.email 
        try:
            send_email(
                mail_to=[owner_email],
                cc_list=[],
                bcc_list=[],
                subject=f"[{shop.shop_name} Contact Form] {subject}",
                template='emails/shop_contact_notification.html', 
                context=email_context
            )
            
            ShopNotification.objects.create(
                shop=shop,
                title=f"New Contact Message from {name}",
                message=f"Subject: {subject}\n\nMessage: {message_body}\nReply to: {email}"
            )
            
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, "Failed to send message. Please try again later.")
            
        return redirect('contact_us', shop_slug=shop.shop_slug)

    context = {
        'shop': shop,
    }
    return render(request, 'customer_site/contact_us.html', context)