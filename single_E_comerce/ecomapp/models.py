from django.db import models
from single_E_comerce import settings

class CustomerAddress(models.Model):
    ADDRESS_TYPES = (
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    )
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100) 
    full_address = models.TextField() 
    is_default = models.BooleanField(default=False) 

    class Meta:
        db_table = 'customer_addresses'

class ProductVariant(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='variants')
    attribute_name = models.CharField(max_length=50) # e.g., 'Color', 'Size'
    attribute_value = models.CharField(max_length=50) # e.g., 'Red', 'XL'
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # ভেরিয়েন্টের আলাদা দাম থাকলে
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'product_variants'

class ShopContactMessage(models.Model):
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='messages')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shop_contact_messages'

class ProductViewHistory(models.Model):
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customer_view_history'
        ordering = ['-viewed_at']

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'customer_search_history'
    def __str__(self):
        return self.query
    
class ShopFollower(models.Model):
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.CASCADE)
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'shop')
        db_table = 'shop_followers'

class CouponUsage(models.Model):
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.CASCADE)
    coupon = models.ForeignKey('shops.Coupon', on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coupon_usage'