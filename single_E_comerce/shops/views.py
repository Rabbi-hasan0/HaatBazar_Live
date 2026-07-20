from datetime import timedelta

from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Events, EventActivity, Shop, ShopActivityLog, Coupon, CouponActivityLog, ShopSocialMedia, ShopSubscription, ShopMedia, ShopNotification
from products.models import Product
from orders.models import Order
from .forms import EventForm, ShopSettingsForm, CouponForm, ShopSocialMediaForm, ShopMediaForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, F, Sum
from django.http import JsonResponse

@login_required
def owner_base(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    context = {
        'shop': shop
    }
    return render(request, 'owner_base.html', context)

def get_unread_count_api(request, shop_slug=None):
    if request.user.is_authenticated:
        try:
            if shop_slug and shop_slug != 'dashboard' and shop_slug != 'undefined':
                shop = Shop.objects.get(shop_slug=shop_slug, owner__user=request.user)
            else:
                shop = Shop.objects.filter(owner__user=request.user).first()
            
            if shop:
                count = ShopNotification.objects.filter(shop=shop, is_read=False).count()
                return JsonResponse({'unread_count': count, 'shop_slug': shop.shop_slug})
        except Shop.DoesNotExist:
            pass
            
    return JsonResponse({'unread_count': 0, 'shop_slug': ''})

@login_required
def shop_notifications(request, shop_slug):
    shop = get_object_or_404(Shop, shop_slug=shop_slug, owner__user=request.user)
    
    # --- ইনলাইন এবং বাল্ক অ্যাকশন হ্যান্ডলার (POST Request) ---
    if request.method == "POST":
        action = request.POST.get('action')
        notification_ids = request.POST.getlist('notification_ids')
        
        # যদি একক কোনো নোটিফিকেশনের বাটনে ক্লিক করা হয়
        single_id = request.POST.get('notification_id')
        if single_id:
            notification_ids = [single_id]
            
        if notification_ids:
            target_notifications = ShopNotification.objects.filter(shop=shop, id__in=notification_ids)
            
            if action == 'read':
                target_notifications.update(is_read=True)
                messages.success(request, f"{target_notifications.count()}টি নোটিফিকেশন পঠিত হিসেবে চিহ্নিত হয়েছে।")
            elif action == 'delete':
                count = target_notifications.count()
                target_notifications.delete()
                messages.success(request, f"{count}টি নোটিফিকেশন সফলভাবে ডিলিট করা হয়েছে।")
                
        return redirect('shop_notifications', shop_slug=shop.shop_slug)

    all_notifications = ShopNotification.objects.filter(shop=shop)
    unread_notifications = all_notifications.filter(is_read=False)
    
    alert_notifications = all_notifications.filter(title__icontains='Alert') | all_notifications.filter(title__icontains='Warning')
    
    context = {
        'shop': shop,
        'notifications': all_notifications,
        'unread_notifications': unread_notifications,
        'alert_notifications': alert_notifications,
        'unread_count': unread_notifications.count(),
        'alerts_count': alert_notifications.count(),
    }
    return render(request, 'notifications/shop_notification.html', context)

def shop_owner_dashboard(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    
    #shop operational status check
    current_subscription = getattr(shop, 'current_subscription', None)
    plan = current_subscription.plan if current_subscription else None
    
    now = timezone.now()
    active_coupons_count = Coupon.objects.filter(
        shop=shop,
        is_active=True,
        valid_from__lte=now,
        valid_to__gte=now
    ).count()
    active_events_count = Events.objects.filter(
        shop=shop,
        start_time__lte=now,
        end_time__gte=now
    ).count()
    stock_data = Product.objects.filter(shop=shop, is_active=True).aggregate(total=Sum('stock'))
    total_stock = stock_data['total'] or 0
    total_investment = Product.objects.filter(shop=shop, is_active=True).aggregate(
        total=Sum(F('price') * F('stock'))
    )['total'] or 0
    recent_logs = ShopActivityLog.objects.filter(shop=shop)[:10]
    product_count = total_stock 
    order_count = Order.objects.filter(shop=shop).count()
    product_percentage = (product_count / plan.product_limit * 100) if plan and plan.product_limit else 0
    order_percentage = (order_count / plan.order_limit * 100) if plan and plan.order_limit else 0
    
    days_left = None
    if current_subscription:
        days_left = (current_subscription.expire_date - timezone.now().date()).days
        
    #Todays operations summary
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders_count = Order.objects.filter(
        shop=shop, 
        created_at__gte=today_start
    ).count()
    today_gross_sales = Order.objects.filter(
        shop=shop, 
        created_at__gte=today_start
    ).aggregate(total=Sum('grand_total'))['total'] or 0
    today_deliveries_count = Order.objects.filter(
        shop=shop, 
        status='delivered',
        updated_at__gte=today_start 
    ).count()
    # today_revenue = today_deliveries_count.aggregate(total=Sum('grand_total'))['total'] or 0
    today_net_profit = float(today_gross_sales) * 0.07
    
    one_month_ago = now - timedelta(days=30)
    last_month_orders = Order.objects.filter(shop=shop, created_at__gte=one_month_ago, status='delivered')
    last_month_profit = last_month_orders.aggregate(total=Sum('grand_total'))['total'] or 0
    last_month_loss_data = last_month_orders.aggregate(
        normal_disc=Sum('discount'),
        coupon_disc=Sum('coupon_discount')
    )
    last_month_loss = (last_month_loss_data['normal_disc'] or 0) + (last_month_loss_data['coupon_disc'] or 0)

    # ----------- LAST YEAR BALANCE (গত ৩৬৫ দিন) -----------
    one_year_ago = now - timedelta(days=365)
    last_year_orders = Order.objects.filter(shop=shop, created_at__gte=one_year_ago, status='delivered')
    last_year_profit = last_year_orders.aggregate(total=Sum('grand_total'))['total'] or 0
    last_year_loss_data = last_year_orders.aggregate(
        normal_disc=Sum('discount'),
        coupon_disc=Sum('coupon_discount')
    )
    last_year_loss = (last_year_loss_data['normal_disc'] or 0) + (last_year_loss_data['coupon_disc'] or 0)


    # ----------- TOTAL CUMULATIVE BALANCE (অল-টাইম) -----------
    all_time_orders = Order.objects.filter(shop=shop, status='delivered')
    total_net_profit = all_time_orders.aggregate(total=Sum('grand_total'))['total'] or 0
    all_time_loss_data = all_time_orders.aggregate(
        normal_disc=Sum('discount'),
        coupon_disc=Sum('coupon_discount')
    )
    total_business_loss = (all_time_loss_data['normal_disc'] or 0) + (all_time_loss_data['coupon_disc'] or 0)

    context = {
        'shop': shop,
        'subscription': current_subscription,
        'plan': plan,
        'days_left': days_left,
        'active_events_count': active_events_count,
        'active_coupons_count': active_coupons_count,
        'recent_logs': recent_logs,
        'product_count': product_count,
        'order_count': order_count,
        'product_percentage': product_percentage,
        'order_percentage': order_percentage,
        'total_stock': total_stock,
        'total_investment': total_investment,
        'today_orders_count': today_orders_count,
        'today_gross_sales': today_gross_sales,
        'today_deliveries_count': today_deliveries_count,
        'today_net_profit': today_net_profit,
        'last_month_profit': last_month_profit,
        'last_month_loss': last_month_loss,
        'last_year_profit': last_year_profit,
        'last_year_loss': last_year_loss,
        'total_net_profit': total_net_profit,
        'total_business_loss': total_business_loss,
    }
    return render(request, 'shops/others/dashboard.html', context)

def shop_settings_update(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    if request.method == 'POST':
        form = ShopSettingsForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfull!")
            return redirect('shop_profile_update')
    else:
        form = ShopSettingsForm(instance=shop)
    return render(request, 'shops/others/shop_settings.html', {'form': form, 'shop': shop})

#----------------------------------------------------Cupon--------------------------------------------------#
@login_required
def coupon_list(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    coupons = shop.shop_coupons.all().order_by('-id')  # নতুন কুপনগুলো যেন উপরে থাকে
    context = {
        'coupons': coupons,
        'shop': shop
    }
    return render(request, 'shops/coupon/coupon_list.html', context)

@login_required
def coupon_create(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.shop = shop  
            coupon.save()
            
            # --- অ্যাক্টিভিটি লগ (CREATE) ---
            discount_type = f"{coupon.discount_amount}%" if coupon.is_percentage else f"${coupon.discount_amount}"
            CouponActivityLog.objects.create(
                shop=shop,
                user=shop.owner,  # <--- এখানে request.user এর বদলে shop.owner হবে
                coupon_code=coupon.code,
                action='CREATE',
                details=f"Created a new coupon code '{coupon.code}' with a discount value of {discount_type}."
            )
            
            messages.success(request, f"New coupon '{coupon.code}' created successfully.")
            return redirect('coupon_list')
    else:
        form = CouponForm()
    return render(request, 'shops/coupon/coupon_form.html', {'form': form, 'shop': shop})

@login_required
def coupon_update(request, pk):
    shop = get_object_or_404(Shop, owner__user=request.user)
    coupon = get_object_or_404(Coupon, pk=pk, shop=shop)
    
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            
            # --- অ্যাক্টিভিটি লগ (EDIT) ---
            discount_type = f"{coupon.discount_amount}%" if coupon.is_percentage else f"${coupon.discount_amount}"
            CouponActivityLog.objects.create(
                shop=shop,
                user=shop.owner,  # <--- এখানে request.user এর বদলে shop.owner হবে
                coupon_code=coupon.code,
                action='EDIT',
                details=f"Updated coupon settings for '{coupon.code}'. Current discount: {discount_type}. Status: {'Active' if coupon.is_active else 'Inactive'}."
            )
            
            messages.success(request, f"Coupon '{coupon.code}' updated successfully!")
            return redirect('coupon_list')
    else:
        form = CouponForm(instance=coupon)
        
    return render(request, 'shops/coupon/coupon_form.html', {
        'form': form, 
        'shop': shop, 
        'is_edit': True,
        'coupon': coupon
    })

@login_required
@require_POST
def coupon_delete(request, pk):
    shop = get_object_or_404(Shop, owner__user=request.user)
    coupon = get_object_or_404(Coupon, pk=pk, shop=shop)
    coupon_code = coupon.code
    CouponActivityLog.objects.create(
        shop=shop,
        user=shop.owner, 
        coupon_code=coupon_code,
        action='DELETE',
        details=f"Permanently deleted the coupon code '{coupon_code}'."
    )
    coupon.delete()
    messages.success(request, f"Coupon '{coupon_code}' deleted successfully!")
    return redirect('coupon_list')

def active_coupons_list(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    now = timezone.now()
    active_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_to__gte=now
    )
    context={
        'shop': shop,
        'active_coupons': active_coupons
    }
    return render(request, 'shops/coupon/active_coupons.html', context)

def coupon_history_list(request):
    now = timezone.now()
    expired_coupons = Coupon.objects.filter(
        is_active=False,
        valid_to__lt=now
    )
    context = {
        'shop': get_object_or_404(Shop, owner__user=request.user),
        'coupons': expired_coupons
    }
    return render(request, 'shops/coupon/coupon_history.html', context)

def coupon_activity_logs(request):
    logs = CouponActivityLog.objects.all()
    context = {
        'shop': get_object_or_404(Shop, owner__user=request.user),
        'logs': logs
    }
    return render(request, 'shops/coupon/activity_logs.html', context)

#----------------------------------------------------Events--------------------------------------------------#
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def events_list(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    events = shop.shop_app_events.all().order_by('-created_at')
    context = {
        'shop': shop,
        'events': events,
        'page_title': 'All Events List'
    }
    return render(request, 'shops/events/event_list.html', context)

@login_required
def add_event(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.shop = shop
            event.save()
            form.save_m2m()
            EventActivity.objects.create(
                event=event,
                event_title_backup=event.title,
                user=request.user,
                action='create',
                changes_logged=f"Event created with status: {event.status}",
                ip_address=get_client_ip(request)
            )
            messages.success(request, "Event created successfully!")
            return redirect('events_list')
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'title': 'Add New Event',
        'shop': shop
    }
    return render(request, 'shops/events/event_form.html', context)

@login_required
def edit_event(request, id):
    shop = get_object_or_404(Shop, owner__user=request.user)
    event = get_object_or_404(Events, id=id, shop=shop)
    old_status = event.status
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            updated_event = form.save()
            action_type = 'update'
            log_msg = "Event details updated."
            if old_status != updated_event.status:
                if updated_event.status == 'active':
                    action_type = 'activate'
                    log_msg = f"Event status changed from {old_status} to Active."
                elif updated_event.status in ['draft', 'expired']:
                    action_type = 'deactivate'
                    log_msg = f"Event status changed from {old_status} to {updated_event.status.capitalize()}."
            EventActivity.objects.create(
                event=updated_event,
                event_title_backup=updated_event.title,
                user=request.user,
                action=action_type,
                changes_logged=log_msg,
                ip_address=get_client_ip(request)
            )
            messages.success(request, "Event updated successfully!")
            return redirect('events_list')
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'title': 'Edit Event',
        'event': event
    }
    return render(request, 'shops/events/event_form.html', context)

@login_required
def delete_event(request, id):
    shop = get_object_or_404(Shop, owner__user=request.user)
    event = get_object_or_404(Events, id=id, shop=shop)
    if request.method == 'POST':
        EventActivity.objects.create(
            event=None,
            event_title_backup=event.title,
            user=request.user,
            action='delete',
            changes_logged=f"Event ID {event.id} was permanently deleted.",
            ip_address=get_client_ip(request)
        )
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('events_list')
    return redirect('events_list')

@login_required
def active_events(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    now = timezone.now()
    events = Events.objects.filter(
        shop=shop,
        status='active',
        start_time__lte=now,
        end_time__gte=now
    ).order_by('-created_at')
    context = {
        'shop': shop,
        'events': events,
        'page_title': 'Active Events'
    }
    return render(request, 'shops/events/event_list.html', context)

@login_required
def upcoming_events(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    now = timezone.now()
    events = Events.objects.filter(
        shop=shop,
        start_time__gt=now
    ).exclude(status='expired').order_by('-created_at')
    context = {
        'shop': shop,
        'events': events,
        'page_title': 'Upcoming Events'
    }
    return render(request, 'shops/events/event_list.html', context)

@login_required
def event_history(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    now = timezone.now()
    events = Events.objects.filter(shop=shop).filter(
        models.Q(status='expired') | models.Q(end_time__lt=now)
    ).order_by('-created_at')
    context = {
        'shop': shop,
        'events': events,
        'page_title': 'Event History (Expired)'
    }
    return render(request, 'shops/events/event_list.html', context)

@login_required
def activity_events_log(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    activities = EventActivity.objects.filter(
        models.Q(event__shop=shop) | models.Q(event=None)
    ).order_by('-created_at')
    context = {
        'shop': shop,
        'activities': activities,
        'page_title': 'Activity Events Log'
    }
    return render(request, 'shops/events/event_activity_logs.html', context)

#----------------------------------------------------Social--------------------------------------------------#
def social_links_list(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    links = shop.social_links.all() # related_name='social_links'
    return render(request, 'shops/social/social_list.html', {'links': links, 'shop': shop})

def social_link_create(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    if request.method == 'POST':
        form = ShopSocialMediaForm(request.POST)
        if form.is_valid():
            social_link = form.save(commit=False)
            social_link.shop = shop  
            social_link.save()
            messages.success(request, f"'{social_link.platform_name}' link added successfully!")
            return redirect('social_links_list')
    else:
        form = ShopSocialMediaForm()
    return render(request, 'shops/social/social_form.html', {'form': form, 'shop': shop})

@require_POST
def social_link_delete(request, pk):
    shop = get_object_or_404(Shop, owner__user=request.user)
    social_link = get_object_or_404(ShopSocialMedia, pk=pk, shop=shop)
    platform = social_link.platform_name
    social_link.delete()
    messages.success(request, f"'{platform}' linked removed successfully!")
    return redirect('social_links_list')

#----------------------------------------------------Media--------------------------------------------------#
@login_required
def shop_media_list(request):
    shop = get_object_or_404(
        Shop.objects.select_related('owner__user'), 
        owner__user=request.user
    )
    media_items = shop.shop_media.all().order_by('-created_at')
    return render(request, 'shops/media/media_list.html', {'media_items': media_items, 'shop': shop})

@login_required
def shop_media_create(request):
    shop = get_object_or_404(
        Shop.objects.select_related('owner__user'), 
        owner__user=request.user
    )
    
    if request.method == 'POST':
        form = ShopMediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.shop = shop
            media.save()
            messages.success(request, f"'{media.title}' Media uploaded successfully!")
            return redirect('shop_media_list')
    else:
        form = ShopMediaForm()
        
    return render(request, 'shops/media/media_form.html', {'form': form, 'shop': shop})

@login_required
@require_POST
def shop_media_delete(request, pk):
    shop = get_object_or_404(
        Shop.objects.select_related('owner__user'), 
        owner__user=request.user
    )
    media = get_object_or_404(ShopMedia, pk=pk, shop=shop)
    
    title = media.title
    media.delete()
    
    messages.success(request, f"'{title}' Media is deleted!")
    return redirect('shop_media_list')


#----------------------------------------------------Subscription--------------------------------------------------#
@login_required
def subscription_billing(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    subscriptions = ShopSubscription.objects.filter(shop=shop).order_by('-start_date')
    active_subscription = subscriptions.filter(is_active=True).first()
    return render(request, 'shops/others/billing.html', {
        'shop': shop,
        'subscriptions': subscriptions,
        'active_subscription': active_subscription
    })

@login_required
def activity_logs_list(request):
    shop = get_object_or_404(Shop, owner__user=request.user)
    logs = ShopActivityLog.objects.filter(shop=shop).order_by('-created_at')    
    return render(request, 'shops/others/activity_logs.html', {
        'shop': shop,
        'logs': logs
    })