# from django.contrib import admin
# from django.utils.timezone import now
# from orders.models import Order, OrderDetail, OrderCart

# admin.site.register(OrderCart)
# class OrderDetailInline(admin.TabularInline):
#     model = OrderDetail
#     extra = 0
#     readonly_fields = ('product', 'unit_price', 'quantity', 'total_price')
#     can_delete = False

# # মূল অ্যাডমিন ক্লাস যা সব পেজের জন্য কমন লজিক রাখবে
# class BaseOrderAdmin(admin.ModelAdmin):
#     list_display = [
#         'order_number', 'get_customer_name', 'get_payment_status', 
#         'get_payment_type', 'get_transaction_id', 'created_at', 
#         'status', 'get_phone', 'billing_address'
#     ]
#     inlines = [OrderDetailInline]
#     list_filter = ['status', 'created_at']
#     search_fields = ['order_number', 'customer__name', 'customer__phone']

#     # কাস্টম মেথডসমূহ ডেটা দেখানোর জন্য
#     def get_customer_name(self, obj):
#         return obj.customer.user.first_name
#     get_customer_name.short_description = 'Customer Name'

#     def get_phone(self, obj):
#         return obj.customer.phone
#     get_phone.short_description = 'Phone'

#     def get_payment_status(self, obj):
#         # OnlinePaymentRequest থেকে স্ট্যাটাস চেক
#         payment = obj.order_payment_requests.last()
#         return payment.payment_status if payment else "Not Initiated"
#     get_payment_status.short_description = 'Payment Status'

#     def get_payment_type(self, obj):
#         payment = obj.order_payment_requests.last()
#         return payment.card_type if payment else "N/A"
#     get_payment_type.short_description = 'Payment Type'

#     def get_transaction_id(self, obj):
#         payment = obj.order_payment_requests.last()
#         return payment.transaction_id if payment else "N/A"
#     get_transaction_id.short_description = 'Transaction ID'

# # --- ১. New Order (আজকের অর্ডার) ---
# class NewOrder(Order):
#     class Meta:
#         proxy = True
#         verbose_name = 'New Order'
#         verbose_name_plural = '1. New Orders'

# @admin.register(NewOrder)
# class NewOrderAdmin(BaseOrderAdmin):
#     def get_queryset(self, request):
#         from datetime import date
#         return super().get_queryset(request).filter(created_at__date=date.today())

# # --- ২. Pending Order ---
# class PendingOrder(Order):
#     class Meta:
#         proxy = True
#         verbose_name = 'Pending Order'
#         verbose_name_plural = '2. Pending Orders'

# @admin.register(PendingOrder)
# class PendingOrderAdmin(BaseOrderAdmin):
#     def get_queryset(self, request):
#         return super().get_queryset(request).filter(status='pending')

# # --- ৩. Complete Order ---
# class CompleteOrder(Order):
#     class Meta:
#         proxy = True
#         verbose_name = 'Complete Order'
#         verbose_name_plural = '3. Complete Orders'

# @admin.register(CompleteOrder)
# class CompleteOrderAdmin(BaseOrderAdmin):
#     def get_queryset(self, request):
#         return super().get_queryset(request).filter(status='delivered')

# # --- ৪. Total Order ---
# @admin.register(Order)
# class TotalOrderAdmin(BaseOrderAdmin):
#     # এটি ডিফল্ট Order মডেল ব্যবহার করবে সব দেখার জন্য
#     pass