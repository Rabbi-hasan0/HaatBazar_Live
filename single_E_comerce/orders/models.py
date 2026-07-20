from django.db import models
from accounts.models import CustomerProfile, ShopOwnerProfile
from products.models import Product
from django.utils import timezone
import datetime
from single_E_comerce import settings

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    shop            = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='orders', db_index=True)
    order_number    = models.CharField(max_length=100, blank=True, null=True)
    customer        = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, db_index=True)
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_amount    = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    shipping_charge = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    shipping_address= models.CharField(max_length=255, blank=True, null=True)
    discount        = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    coupon_discount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    vat_amount      = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    tax_amount      = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    paid_amount     = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    due_amount      = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    grand_total     = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.order_number)+" ("+str(self.customer)+" - "+str(self.created_at)+")"

    class Meta:
        db_table = 'orders'
        indexes = [
            models.Index(fields=['shop']),
            models.Index(fields=['customer']),
        ]
    def save(self, *args, **kwargs):
        subtotal = float(self.order_amount) + float(self.shipping_charge) + float(self.vat_amount) + float(self.tax_amount)
        total_discount = float(self.discount) + float(self.coupon_discount)
        self.grand_total = max(0, subtotal - total_discount)
        self.due_amount = max(0, float(self.grand_total) - float(self.paid_amount))
        if not self.order_number:
            import datetime 
            current_year = datetime.date.today().year
            current_month = datetime.date.today().month
            current_day = datetime.date.today().day
            current_customer_id = self.customer.id

            last_order = Order.objects.filter(order_number__startswith=f"{current_year}{current_month:02d}")

            increase_number = 1
            new_order_number = f"{current_year}{current_month:02d}{last_order.count() + increase_number:04d}{current_day:02d}{current_customer_id}"

            while Order.objects.filter(order_number=new_order_number).exists():
                increase_number += 1
                new_order_number = f"{current_year}{current_month:02d}{last_order.count() + increase_number:04d}{current_day:02d}{current_customer_id}"

            self.order_number = new_order_number
            
        from django.utils import timezone 
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='order_details', on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    unit_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    is_discount = models.BooleanField(default=False)
    discount_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order.order_number)+" ("+str(self.product)+" - "+str(self.quantity)+")"
    class Meta:
        db_table = 'order_details'

class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20) # e.g., Shipped, Delivered
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True, null=True) 

    class Meta:
        db_table = 'order_status_logs'

class OrderCart(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE,related_name='order_cart', db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    is_order= models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def total_amount(self):
        return_value=float(self.quantity) * float(self.product.price)
        return return_value
    class Meta:
        db_table = 'order_cart'
    def __str__(self):
        return f"{self.customer} - {self.product.product_name} ({self.quantity})"

class OrderPayment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHODS = (
        ('cod', 'Cash On Delivery'),
        ('online', 'Online Payment')
    )
    order = models.ForeignKey('orders.Order', related_name='payments', on_delete=models.CASCADE)
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE) 

    payment_status  = models.CharField(max_length=20,choices=PAYMENT_STATUS, default='pending')
    payment_method  = models.CharField(max_length=50, blank=True, null=True)
    payment_type    = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='cod')
    amount          = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    transaction_id  = models.CharField(max_length=50, blank=True, null=True)
    is_active       = models.BooleanField(default=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'order_payments'
    def __str__(self):
        return str(self.order.order_number)+" ("+str(self.payment_method)+" - "+str(self.amount)+")"
