from email.utils import quote

from django.http import JsonResponse
from decimal import Decimal
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from orders.models import OrderCart, Order, OrderDetail, OrderPayment, OrderStatusLog
from accounts.models import CustomerProfile, ShopOwnerProfile
from products.models import Product
from shops.models import Shop
from single_E_comerce import settings
from .views_payment import create_payment_request


def paginate_data(request, page_num, data_list):
    items_per_page, max_pages = 10, 10
    paginator = Paginator(data_list, items_per_page)
    last_page_number = paginator.num_pages

    try:
        data_list = paginator.page(page_num)
    except PageNotAnInteger:
        data_list = paginator.page(1)
    except EmptyPage:
        data_list = paginator.page(paginator.num_pages)

    current_page = data_list.number
    start_page = max(current_page - int(max_pages / 2), 1)
    end_page = start_page + max_pages

    if end_page > last_page_number:
        end_page = last_page_number + 1
        start_page = max(end_page - max_pages, 1)

    paginator_list = range(start_page, end_page)
    return data_list, paginator_list, last_page_number

@login_required
def cart_amount_summary(request):
    sub_total_amount = Decimal('0.00')
    total_vat = Decimal('0.00')
    total_discount = Decimal('0.00')
    grand_total = Decimal('0.00')

    if request.user.is_authenticated:
        customer = CustomerProfile.objects.filter(user=request.user).first()
        
        if customer:
            cart_items = OrderCart.objects.filter(
                customer=customer, 
                is_active=True, 
                is_order=False
            ).select_related('product')
            
            for item in cart_items:
                sub_total_amount += Decimal(str(item.total_amount))

    grand_total = (sub_total_amount + total_vat) - total_discount 

    return {
        'sub_total_amount': sub_total_amount, 
        'total_vat': total_vat, 
        'total_discount': total_discount, 
        'grand_total': grand_total
    }     

def cart_view(request, shop_slug):
    if not request.user.is_authenticated:
        return redirect('customer_login')
    
    customer = CustomerProfile.objects.filter(user=request.user).first()
    current_shop = get_object_or_404(Shop, shop_slug=shop_slug)
    
    cart_items = OrderCart.objects.filter(
        customer=customer, 
        product__shop=current_shop, 
        is_active=True, 
        is_order=False
    ).select_related('product__shop')
    
    grouped_cart = {}
    if cart_items.exists():
        grouped_cart[current_shop] = list(cart_items)
        
    sub_total_amount = sum(Decimal(str(item.total_amount)) for item in cart_items)
    total_vat = Decimal('0.00')
    total_discount = Decimal('0.00')
    grand_total = (sub_total_amount + total_vat) - total_discount
    
    context = {
        'shop': current_shop,
        'grouped_cart': grouped_cart,
        'cart_items': cart_items,
        'sub_total_amount': sub_total_amount,
        'total_vat': total_vat,
        'total_discount': total_discount,
        'grand_total': grand_total,
    }
    return render(request, 'cart/customer_cart.html', context)


def add_or_update_cart(request, shop_slug):
    if not request.user.is_authenticated:
        next_url = request.META.get('HTTP_REFERER', '/')
        login_url = f"{reverse('customer_login')}?next={quote(next_url)}"

        return JsonResponse({
            'status': 'unauthenticated', 
            'message': 'User not authenticated', 
            'is_authenticated': False,
            'redirect_url': login_url
        }, status=401)
    
    if request.method == 'POST':
        try:
            customer = CustomerProfile.objects.filter(user=request.user).first()
            if not customer:
                return JsonResponse({'status': 'error', 'message': 'Customer not found'}, status=404)
            product_id = request.POST.get('product_id')
            quantity_raw = request.POST.get('quantity')
            
            with transaction.atomic():
                existing_item = OrderCart.objects.filter(customer=customer, product_id=product_id, is_order=False).first()
                duplicates = OrderCart.objects.filter(customer=customer, product_id=product_id, is_order=False)
                if duplicates.count() > 1:
                    duplicates.delete()
                    existing_item = None

                if quantity_raw is not None:
                    quantity = int(quantity_raw)
                else:
                    quantity = (existing_item.quantity + 1) if existing_item else 1

                is_active_status = True if quantity > 0 else False
                isRemoved = True if quantity <= 0 else False
                
                cart_item, created = OrderCart.objects.update_or_create(
                    customer=customer, 
                    product_id=product_id, 
                    is_order=False, 
                    defaults={
                        'quantity': quantity,
                        'is_active': is_active_status, 
                    }
                )
            product = cart_item.product
            product_name = product.product_name if product else "N/A"
            product_price = product.price if product else 0
            
            if product and product.product_image:
                product_image_url = product.product_image.url
            else:
                product_image_url = None

            amount_summary = cart_amount_summary(request)
            cart_item_count = OrderCart.objects.filter(customer=customer, is_order=False, is_active=True).count()
            return JsonResponse({
                'status': 'success',
                'message': 'Product added to cart successfully',
                'is_authenticated': True,
                'isRemoved': isRemoved,
                'cart_item_count': cart_item_count,
                'amount_summary': amount_summary,
                'product_name': product_name,
                'quantity': cart_item.quantity,
                'product_price': float(product_price),
                'total_amount': float(cart_item.total_amount if hasattr(cart_item, 'total_amount') else (product_price * cart_item.quantity)),
                'product_image_url': product_image_url,
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'is_authenticated': True}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request', 'is_authenticated': True}, status=400)

@login_required
def remove_from_cart(request, shop_slug, item_id): 
    customer = CustomerProfile.objects.filter(user=request.user).first()
    cart_item = get_object_or_404(OrderCart, id=item_id, customer=customer)
    cart_item.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        active_shop_cart = OrderCart.objects.filter(
            customer=customer, 
            product__shop__shop_slug=shop_slug, 
            is_order=False, 
            is_active=True
        )
        
        sub_total = sum(Decimal(str(item.total_amount)) for item in active_shop_cart)
        vat = Decimal('0.00')
        discount = Decimal('0.00')
        grand_total = (sub_total + vat) - discount
        
        global_cart_count = OrderCart.objects.filter(
            customer=customer, 
            is_order=False, 
            is_active=True
        ).count()
        
        return JsonResponse({
            'status': 'success',
            'cart_item_count': global_cart_count, # নেভবারের কাউন্টার
            'shop_item_count': active_shop_cart.count(), # টেমপ্লেট হাইড করার জন্য
            'amount_summary': {
                'sub_total_amount': f"{sub_total:.2f}",
                'total_vat': f"{vat:.2f}",
                'total_discount': f"{discount:.2f}",
                'grand_total': f"{grand_total:.2f}"
            }
        })
    return redirect('cart_view', shop_slug=shop_slug)

@login_required
def checkout(request):
    amount_summary = cart_amount_summary(request)
    grand_total = amount_summary.get('grand_total', Decimal('0.00'))

    if grand_total < 1:
        messages.error(request, "Your cart is empty. Please add items to your cart before proceeding to checkout.")
        return redirect('cart')
    
    if request.method == 'POST':
        with transaction.atomic():
            billing_address = request.POST.get('billing_address')
            customer = CustomerProfile.objects.filter(user=request.user).first()

            if not billing_address:
                messages.error(request, "Billing address is required.")
                return redirect('checkout')
                
            cart_items = OrderCart.objects.filter(customer=customer, is_active=True, is_order=False).select_related('product__shop')

            if not cart_items.exists():
                messages.error(request, "Your cart is empty. Please add items to your cart before proceeding to checkout.")
                return redirect('cart')
            
            first_shop = cart_items.first().product.shop

            order_obj = Order.objects.create(
                shop=first_shop,
                customer=customer,
                billing_address=billing_address,
            )
            
            order_amount = Decimal('0.00')
            shipping_charge = Decimal('0.00')
            discount = Decimal('0.00')
            coupon_discount = Decimal('0.00')
            vat_amount = Decimal('0.00')
            tax_amount = Decimal('0.00')
            
            for cart_item in cart_items:
                item_total = Decimal(str(cart_item.total_amount))
                order_amount += item_total
                
                OrderDetail.objects.create(
                    order=order_obj,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price,
                    total_price=item_total
                )

            order_obj.order_amount = order_amount
            order_obj.shipping_charge = shipping_charge
            order_obj.discount = discount
            order_obj.coupon_discount = coupon_discount
            order_obj.vat_amount = vat_amount
            order_obj.tax_amount = tax_amount
            order_obj.save()

            messages.success(request, "Order placed successfully.")

            response_data, response_status = create_payment_request(request, order_obj.id)

            if response_data.get('status') == "SUCCESS":
                for cart_item in cart_items:
                    cart_item.is_order = True
                    cart_item.save()

                return redirect(response_data['GatewayPageURL'])
            elif "error_message" in response_data:
                messages.error(request, response_data['error_message'])
            else:
                messages.error(request, 'Failed to payment.')

            return redirect('home')











