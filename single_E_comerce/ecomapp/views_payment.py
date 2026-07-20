from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.core import signing
from django.db.models import Sum
from django.utils import timezone
from django.conf import settings
import requests
from uuid import uuid4
from payments.models import OnlinePaymentRequest
from orders.models import Order

def create_payment_request(request, order_id):
    transaction_id = str(uuid4())
    order_obj = Order.objects.filter(id=order_id).last()

    if not order_obj:
        return {'status': 'FAILED', 'message': 'Order not found'}, 404

    success_url = request.build_absolute_uri(f'/backend/payment/success/{transaction_id}/')
    fail_url = request.build_absolute_uri(f'/backend/payment/fail/{transaction_id}/')
    cancel_url = request.build_absolute_uri(f'/backend/payment/cancel/{transaction_id}/')

    # ডেটাবেজে পেন্ডিং রিকোয়েস্ট সেভ
    OnlinePaymentRequest.objects.create(
        order=order_obj,
        transaction_id=transaction_id,
        amount=order_obj.grand_total,
        payment_status='Pending',
        created_by=request.user,
    )

    payment_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': order_obj.grand_total,
        'currency': 'BDT',
        'tran_id': transaction_id,
        'success_url': success_url,
        'fail_url': fail_url,
        'cancel_url': cancel_url,
        'cus_name': order_obj.customer.user.first_name,
        'cus_email': order_obj.customer.user.email,
        'cus_phone': order_obj.customer.phone,
        'cus_add1': order_obj.billing_address or 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_name': 'Order Payment',
        'product_category': 'Ecommerce',
        'product_profile': 'general',
    }

    response = requests.post(settings.SSLCOMMERZ_API_URL, data=payment_data)
    data = response.json()

    if data.get('status') == 'SUCCESS':
        return {
            'GatewayPageURL': data['GatewayPageURL'],
            'status': 'SUCCESS',
        }, 200
    else:
        return {
            'status': 'FAILED',
            'message': data.get('failedreason', 'Unknown error occurred')
        }, 400


# # --- ১. পেমেন্ট ভেরিফিকেশন হেল্পার ফাংশন ---
# def verify_ssl_payment(val_id):
#     payload = {
#         'val_id': val_id,
#         'store_id': settings.SSLCOMMERZ_STORE_ID,
#         'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
#         'v': '1',
#         'format': 'json'
#     }
#     try:
#         response = requests.get(settings.SSLCOMMERZ_VALIDATION_API, params=payload)
#         result = response.json()
#         # SSL থেকে VALID অথবা VALIDATED স্ট্যাটাস আসলে ডাটা রিটার্ন করবে
#         if result.get('status') in ['VALID', 'VALIDATED']:
#             return result
#     except Exception as e:
#         print(f"SSL Verification Error: {e}")
#     return None


# # --- ২. পেমেন্ট এন্ট্রি পয়েন্ট (এপিআই বা ডিরেক্ট কল) ---
# @csrf_exempt
# def payment_create(request):
#     response_data = {}
#     error_message = []

#     try:
#         if request.method == 'POST':
#             order_id = request.POST.get("ecom_order_id", None)
#             payment_method = request.POST.get("payment_method", '')

#             if not order_id:
#                 error_message.append("Please provide order id")
#             if not payment_method:
#                 error_message.append("Please provide payment_method")

#             if all([order_id, payment_method]):
#                 # এখান থেকে মেইন রিকোয়েস্ট ফাংশন কল হবে
#                 data, status_code = create_payment_request(request, order_id)
#                 return JsonResponse(data, status=status_code)

#             response_data.update({
#                 'success': False,
#                 "error_message": error_message
#             })
#         else:
#             response_data.update({
#                 'success': False,
#                 "error_message": f"{request.method} not allowed"
#             })
#     except Exception as e:
#         response_data.update({
#             'success': False,
#             "error_message": f"Error: {e}"
#         })
#     return JsonResponse(response_data, status=400)



# # --- ৪. পেমেন্ট কমপ্লিট (ইউজার ব্রাউজারে ফিরে আসলে) ---
# @csrf_exempt
# def payment_complete(request, str_data):
#     val_id = request.POST.get('val_id')

#     try:
#         payment_object = OnlinePaymentRequest.objects.get(transaction_id=str_data)
#     except OnlinePaymentRequest.DoesNotExist:
#         messages.error(request, "Invalid transaction")
#         return redirect('home')
    
#     if payment_object.payment_status != 'Paid':
#         status_data = verify_ssl_payment(val_id)

#         if status_data: 
#             # পেমেন্ট এবং অর্ডার একবারে আপডেট করার ফাংশন কল
#             update_payment_in_order(str_data, val_id, request.POST)
#             messages.success(request, f"Payment confirmed for order {payment_object.order.id}")
#         else:
#             messages.error(request, "Payment verification failed")
#             return redirect('home')
#     else:
#         messages.success(request, "Your requested payment has already been paid")

#     return redirect('home')


# # --- ৫. WEBHOOK / IPN (ব্যাকগ্রাউন্ডে কনফার্ম করার জন্য) ---
# @csrf_exempt
# def ssl_ipn(request):
#     if request.method == 'POST':
#         tran_id = request.POST.get('tran_id')
#         val_id = request.POST.get('val_id')
#         status = request.POST.get('status')

#         try:
#             payment_object = OnlinePaymentRequest.objects.get(transaction_id=tran_id)
            
#             # যদি স্ট্যাটাস VALID হয় এবং আগে পেইড না হয়ে থাকে
#             if payment_object.payment_status != 'Paid' and status in ['VALID', 'VALIDATED']:
#                 if verify_ssl_payment(val_id):
#                     update_payment_in_order(tran_id, val_id, request.POST)
            
#             return HttpResponse("IPN Processed")
#         except OnlinePaymentRequest.DoesNotExist:
#             return HttpResponse("Transaction Not Found", status=404)

#     return HttpResponse("Invalid Request", status=400)


# # --- ৬. পেমেন্ট এবং অর্ডারের হিসাব আপডেট (কমন ফাংশন) ---
# def update_payment_in_order(transaction_id, val_id, post_data):
#     payment_object = OnlinePaymentRequest.objects.filter(transaction_id=transaction_id).first()

#     if payment_object and payment_object.payment_status != "Paid":
#         # পেমেন্ট রিকোয়েস্ট আপডেট
#         payment_object.payment_status = "Paid"
#         payment_object.val_id = val_id
#         payment_object.bank_tran_id = post_data.get('bank_tran_id')
#         payment_object.card_type = post_data.get('card_type')
#         payment_object.paid_at = timezone.now()
#         payment_object.updated_at = timezone.now()
#         payment_object.save()

#         # অর্ডার পেমেন্ট টেবিলে এন্ট্রি
#         OrderPayment.objects.create(
#             order=payment_object.order, 
#             payment_method="SSL",
#             amount=payment_object.amount, 
#             transaction_id=transaction_id
#         )

#         # অর্ডারের পেইড এবং ডিউ অ্যামাউন্ট আপডেট
#         total_paid = OrderPayment.objects.filter(
#             order=payment_object.order, 
#             is_active=True
#         ).aggregate(total_paid=Sum('amount'))['total_paid'] or 0

#         payment_object.order.paid_amount = total_paid
#         payment_object.order.due_amount = payment_object.order.grand_total - total_paid
#         payment_object.order.save()
#         return True
#     return False


# # --- পেমেন্ট ক্যানসেল এবং ফেইল্ড হ্যান্ডেলার ---
# @csrf_exempt
# def payment_cancel(request, str_data):
#     payment_object = OnlinePaymentRequest.objects.filter(transaction_id=str_data).first()
#     if payment_object and payment_object.payment_status != "Paid":
#         payment_object.payment_status = "Cancelled"
#         payment_object.save()
#     return redirect('home')

# @csrf_exempt
# def payment_failed(request, str_data):
#     payment_object = OnlinePaymentRequest.objects.filter(transaction_id=str_data).first()
#     if payment_object and payment_object.payment_status != "Paid":
#         payment_object.payment_status = "Failed"
#         payment_object.save()
#     return redirect('home')

# # --- পেমেন্ট স্ট্যাটাস চেক (AJAX এর জন্য) ---
# @csrf_exempt
# def payment_check(request, str_data):
#     try:
#         pk = signing.loads(str_data)
#         payment_object = OnlinePaymentRequest.objects.get(id=pk)
#         return JsonResponse({'status': payment_object.payment_status})
#     except:
#         return JsonResponse({'status': 'Invalid'}, status=400)