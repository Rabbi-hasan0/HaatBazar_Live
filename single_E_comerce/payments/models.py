from django.db import models
from django.conf import settings

class OnlinePaymentRequest(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )
    
    PAYMENT_MODE = (
        ('test', 'Test'),
        ('live', 'Live'),
    )

    order = models.ForeignKey('orders.Order', related_name='order_payment_requests', on_delete=models.CASCADE)
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='payment_requests') # related_name ইউনিক করা হয়েছে
    currency = models.CharField(max_length=10, default='BDT')
    store_id = models.CharField(max_length=100, blank=True, null=True)
    payment_mode = models.CharField(max_length=20, default='live', choices=PAYMENT_MODE)
    gateway_name = models.CharField(max_length=50, default='SSLCommerz')
    
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    val_id = models.CharField(max_length=100, blank=True, null=True)
    bank_tran_id = models.CharField(max_length=100, blank=True, null=True)
    card_type = models.CharField(max_length=50, blank=True, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='pending')
    gateway_response = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_requests_created'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "online_payment_request"
        ordering = ['-created_at']

    def __str__(self):
        # অর্ডারের নাম্বার চেক করার সেফটি সহ
        order_number = self.order.order_number if self.order else "N/A"
        return f"{order_number} - {self.payment_status}"