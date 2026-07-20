from django.contrib import admin
from .models import Order, OrderDetail, OrderStatusLog, OrderCart, OrderPayment

# ১. অর্ডারের ভেতরেই প্রোডাক্টের লিস্ট দেখানোর জন্য ইনলাইন কনফিগারেশন
class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    raw_id_fields = ['product'] # প্রোডাক্ট অনেক বেশি হলে যেন সার্চ করা সহজ হয়
    fields = ['product', 'unit_price', 'quantity', 'discount_price', 'total_price', 'is_active']

# ২. অর্ডারের ভেতরেই পেমেন্টের ইনফো দেখানোর জন্য ইনলাইন কনফিগারেশন
class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 0
    fields = ['payment_status', 'payment_method', 'payment_type', 'amount', 'transaction_id', 'payment_date']

# ৩. অর্ডারের ভেতরেই স্ট্যাটাস পরিবর্তনের লগ হিস্ট্রি দেখার জন্য ইনলাইন কনফিগারেশন
class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ['changed_at']
    fields = ['status', 'changed_by', 'note', 'changed_at']


# ৪. মেইন অর্ডার অ্যাডমিন প্যানেল
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # লিস্ট পেজে যে কলামগুলো শো করবে
    list_display = [
        'order_number', 'shop', 'customer', 'status', 
        'grand_total', 'paid_amount', 'due_amount', 'created_at'
    ]
    
    # ডানপাশে কুইক ফিল্টারিং সিস্টেম
    list_filter = ['status', 'is_active', 'created_at', 'shop']
    
    # সার্চ বার (অর্ডার নম্বর, কাস্টমারের ইউজারনেম বা শপের নাম দিয়ে সার্চ করা যাবে)
    search_fields = ['order_number', 'customer__user__username', 'shop__name']
    
    # যেসব ফিল্ড এডিট করা যাবে না (শুধু দেখা যাবে)
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    # অর্ডারের মূল পেজে উপরের ইনলাইন ক্লাসগুলোকে যুক্ত করা হলো
    inlines = [OrderDetailInline, OrderPaymentInline, OrderStatusLogInline]

    # ফর্মের ফিল্ডগুলোকে সুন্দরভাবে সেকশন ওয়াইজ সাজানোর জন্য fieldsets
    fieldsets = (
        ('Order Core Details', {
            'fields': ('order_number', 'shop', 'customer', 'status', 'is_active')
        }),
        ('Financial Breakdowns', {
            'fields': (
                'order_amount', 'shipping_charge', 'discount', 
                'coupon_discount', 'vat_amount', 'tax_amount', 
                'grand_total', 'paid_amount', 'due_amount'
            )
        }),
        ('Shipping & Billing Info', {
            'fields': ('billing_address', 'shipping_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # অ্যাডমিন প্যানেল থেকে যখন কোনো অর্ডারের স্ট্যাটাস চেঞ্জ করা হবে, 
    # তখন যেন অটোমেটিক OrderStatusLog মডেলে একটি ট্র্যাক রেকর্ড জমা হয়
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and 'status' in form.changed_data:
            OrderStatusLog.objects.create(
                order=obj,
                status=obj.status,
                changed_by=request.user,
                note=f"Status manually updated via Django Admin Panel."
            )


# ৫. কাস্টমারদের কার্ট বা ঝুড়ি ট্র্যাক করার জন্য আলাদা অ্যাডমিন
@admin.register(OrderCart)
class OrderCartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'quantity', 'is_order', 'is_active', 'created_at']
    list_filter = ['is_order', 'is_active']
    search_fields = ['customer__user__username', 'product__product_name']


# ৬. পেমেন্টগুলো আলাদাভাবে অডিট করার জন্য ডেডিকেটেড অ্যাডমিন
@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'shop', 'payment_status', 'payment_type', 'amount', 'transaction_id', 'created_at']
    list_filter = ['payment_status', 'payment_type', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']