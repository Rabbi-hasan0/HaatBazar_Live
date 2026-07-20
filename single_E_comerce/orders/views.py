from shops.models import Shop
from .models import Order
from django.db.models import Sum,Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderStatusLog

@login_required
def order_list(request):
    filter_type = request.GET.get('type', 'all')
    base_owner_filter = Q(shop__owner=request.user.shop_owner_profile, is_active=True)
    order_queryset = Order.objects.select_related(
        'customer', 
        'customer__user', 
        'shop'
    ).prefetch_related(
        'payments', 
        'logs' 
    ).filter(base_owner_filter)

    orders = None
    order_activities = None
    if filter_type == 'new':
        time_threshold = timezone.now() - timedelta(hours=24)
        orders = order_queryset.filter(
            created_at__gte=time_threshold
        ).exclude(
            status__in=['delivered', 'cancelled']
        ).order_by('-created_at')
        
    elif filter_type == 'pending':
        orders = order_queryset.filter(status='pending').order_by('-created_at')
        
    elif filter_type == 'activity':
        order_activities = OrderStatusLog.objects.select_related(
            'order', 'changed_by', 'order__shop'
        ).filter(
            order__shop__owner=request.user.shop_owner_profile
        ).order_by('-changed_at')
        
    else:
        orders = order_queryset.order_by('-created_at')
    stats = Order.objects.filter(base_owner_filter).aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('grand_total', filter=Q(status='delivered')), 
        pending_orders=Count('id', filter=Q(status='pending'))
    )

    context = {
        'shop': get_object_or_404(Shop, owner__user=request.user),
        'orders': orders,
        'order_activities': order_activities, 
        'stats': stats,
        'current_filter': filter_type, 
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def order_activity_log(request):
    order_activities = OrderStatusLog.objects.select_related(
        'order', 
        'changed_by', 
        'order__shop'
    ).filter(
        order__shop__owner=request.user.shop_owner_profile
    ).order_by('-changed_at')
    stats = Order.objects.filter(shop__owner=request.user.shop_owner_profile, is_active=True).aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('grand_total', filter=Q(status='delivered')),
        pending_orders=Count('id', filter=Q(status='pending'))
    )
    context = {
        'shop': get_object_or_404(Shop, owner__user=request.user),
        'order_activities': order_activities,
        'stats': stats,
        'current_filter': 'activity',
    }
    return render(request, 'orders/order_activity.html', context)

@login_required
def order_bulk_delete(request):
    if request.method == 'POST':
        order_ids = request.POST.getlist('selected_orders')
        
        if order_ids:
            orders_to_delete = Order.objects.filter(
                id__in=order_ids,
                shop__owner=request.user.shop_owner_profile,
                is_active=True
            )
            count = orders_to_delete.count()
            if count > 0:
                orders_to_delete.update(is_active=False)
                
                messages.success(request, f"Successfully deleted {count} selected orders.")
            else:
                messages.error(request, "No authorized orders found for deletion.")
        else:
            messages.warning(request, "No orders were selected.")
            
    return redirect(request.META.get('HTTP_REFERER', 'order_list'))

@login_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, "Invalid status action.")
        return redirect(request.META.get('HTTP_REFERER','order_list'))
        
    old_status = order.status
    if old_status == new_status:
        messages.info(request, f"Order is already marked as {new_status}.")
        return redirect(request.META.get('HTTP_REFERER','order_list'))
    if new_status == 'delivered':
        order.paid_amount = order.grand_total
        order.due_amount = 0
        payment = order.payments.last()
        if payment:
            payment.payment_status = 'paid'
            payment.payment_date = timezone.now()
            payment.save()
            
    elif new_status == 'cancelled':
        order.due_amount = 0
    order.status = new_status
    order.save()
    OrderStatusLog.objects.create(
        order=order,
        status=new_status,
        changed_by=request.user,
        note=f"Status changed from '{old_status}' to '{new_status}' by shop owner."
    )
    messages.success(request, f"Order #{order.order_number} has been updated to {new_status.upper()}.")
    return redirect(request.META.get('HTTP_REFERER','order_list'))

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related(
            'customer', 'customer__user', 'shop'
        ).prefetch_related(
            'order_details', 'order_details__product', 'payments', 'logs', 'logs__changed_by'
        ), 
        id=order_id
    )
    items = order.order_details.all()
    payments = order.payments.all()
    status_logs = order.logs.all().order_by('-changed_at') 

    context = {
        'shop': get_object_or_404(Shop, owner__user=request.user),
        'order': order,
        'items': items,
        'payments': payments,
        'status_logs': status_logs,
    }
    return render(request, 'orders/order_detail.html', context)