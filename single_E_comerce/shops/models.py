from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify
from single_E_comerce import settings
from admin_management.utils import generate_unique_slug
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product

class Shop(models.Model):
    owner = models.ForeignKey('accounts.ShopOwnerProfile', on_delete=models.CASCADE, related_name='shops', db_index=True)
    # Shop Related Information
    shop_name   = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    shop_type   = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    shop_slug   = models.SlugField(max_length=120, db_index=True, unique=True, null=True, blank=True) 
    shop_logo   = models.ImageField(upload_to='shop_logos/', null=True, blank=True)
    shop_description = models.TextField(null=True, blank=True)
    # Configuration (নতুন সংযোজন)
    currency    = models.CharField(max_length=10, default='BDT')
    timezone    = models.CharField(max_length=50, default='Asia/Dhaka')
    invoice_prefix = models.CharField(max_length=10, blank=True, null=True)
    # Contact & Business Info (Shop specific)
    email       = models.EmailField(null=True, blank=True)
    phone       = models.CharField(max_length=15)
    shop_address= models.TextField()
    trade_license= models.CharField(max_length=100, null=True, blank=True)
    # Verification & Status
    is_active   = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    # Appearance (For Storefront)
    theme_color = models.CharField(max_length=20, default="#000000")
    banner_image= models.ImageField(upload_to='shops/banners/', null=True, blank=True)
    # Meta data
    total_views = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shops'
        verbose_name = "Shop"

    def save(self, *args, **kwargs):
        if not self.shop_slug:
            self.shop_slug = generate_unique_slug(self.shop_name, Shop, 'shop_slug')
        super().save(*args, **kwargs)
    def __str__(self):
        return self.shop_name
    
class ShopActivityLog(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='activity_logs', db_index=True, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='shop_activity_logs')
    module = models.CharField(max_length=50, db_index=True) 
    action = models.CharField(max_length=255) 
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        db_table = 'shop_activity_logs'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.shop.shop_name} - {self.user.username} - {self.action}"
    
class Coupon(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_coupons', db_index=True, null=True, blank=True)
    user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        blank=True, 
        related_name='user_coupons'
    )
    code = models.CharField(max_length=20)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_percentage = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'shop_coupons'
        # unique_together = ('shop', 'code')
    def __str__(self):
        return f"{self.shop.shop_name} - {self.code}"
    @property
    def is_live(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to

class CouponActivityLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Created'),
        ('EDIT', 'Edited'),
        ('DELETE', 'Deleted'),
    )
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='coupon_activities', db_index=True, null=True, blank=True)
    user = models.ForeignKey('accounts.ShopOwnerProfile', on_delete=models.SET_NULL, null=True, blank=True) 
    coupon_code = models.CharField(max_length=50)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True) 

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.coupon_code} - {self.action} by {self.user}"

class Events(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    )
    
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='shop_app_events', db_index=True, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name="Event Title")
    slug = models.SlugField(blank=True, max_length=255) # max_length বাড়ানো হয়েছে
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    banner_desktop = models.ImageField(upload_to='events/desktop/')
    banner_mobile = models.ImageField(upload_to='events/mobile/', null=True, blank=True)
    product = models.ManyToManyField('products.Product', related_name='shop_app_products_events', blank=True) # String reference নিরাপদ
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        constraints = [
            models.UniqueConstraint(fields=['shop', 'slug'], name='unique_shop_event_slug')
        ]

    def __str__(self):
        return f"{self.title} ({self.shop.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            # infinite loop এড়াতে এবং নিখুঁত স্লাগ জেনারেট করতে
            while Events.objects.filter(shop=self.shop, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_running(self):
        now = timezone.now()
        return self.status == 'active' and self.start_time <= now <= self.end_time

    @property
    def time_remaining_seconds(self):
        if self.is_running:
            delta = self.end_time - timezone.now()
            return max(0, int(delta.total_seconds()))
        return 0

class EventActivity(models.Model):
    ACTION_CHOICES = (
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('activate', 'Activated'),
        ('deactivate', 'Deactivated'),
    )

    event = models.ForeignKey(Events, on_delete=models.SET_NULL, null=True, related_name='activities')
    event_title_backup = models.CharField(max_length=255, help_text="Event ডিলিট হয়ে গেলেও যেন নাম ট্র্যাক করা যায়")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Performed By")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changes_logged = models.TextField(blank=True, null=True, help_text="কী কী চেঞ্জ হয়েছে তার ডিটেইলস (ঐচ্ছিক)")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Event Activities"

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{self.event_title_backup} - {self.get_action_display()} by {user_str}"

class ShopSocialMedia(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='social_links', db_index=True, null=True, blank=True)
    platform_name = models.CharField(max_length=50) 
    profile_url = models.URLField()
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'shop_social_media'
    def __str__(self):
        return f"{self.shop.shop_name} - {self.platform_name}"

class ShopMedia(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_media', db_index=True, null=True, blank=True)
    title = models.CharField(max_length=100)
    file = models.ImageField(upload_to='shop_media/')
    media_type = models.CharField(max_length=20, default='Banner') 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shop_media'
    def __str__(self):
        return f"{self.shop.shop_name} - {self.title}"

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Professional'),
    )
    name = models.CharField(max_length=50, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_limit = models.IntegerField(default=50) # লিমিট সেট করা
    order_limit = models.IntegerField(default=100)
    duration_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_name_display()
    class Meta:
        db_table = 'subscription_plans'

class ShopSubscription(models.Model):
    shop = models.OneToOneField('shops.Shop', on_delete=models.CASCADE, related_name='current_subscription')
    plan = models.ForeignKey('shops.SubscriptionPlan', on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField(auto_now_add=True)
    expire_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'shop_subscriptions'
    def __str__(self):
        return f"{self.shop.shop_name} - {self.plan.name}"
    def save(self, *args, **kwargs):
        if not self.pk and not self.expire_date:
            today = timezone.now().date()
            self.expire_date = today + timedelta(days=self.plan.duration_days)
            
        super().save(*args, **kwargs)
        
class ShopNotification(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='notifications', db_index=True, null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at'] 
    def __str__(self):
        return f"Notification for {self.shop.shop_name} - {self.title}"
    
class ShopReview(models.Model):
    shop = models.ForeignKey(
        'Shop', 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Target Shop"
    )
    customer = models.ForeignKey(
        'accounts.CustomerProfile', 
        on_delete=models.CASCADE, 
        related_name='customer_reviews',
        verbose_name="Reviewer"
    )
    
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5"
    )
    comment = models.TextField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="Write your review here (max 500 characters)"
    )
    is_visible = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Is Visible on Site"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shop_reviews'
        ordering = ['-created_at'] 
        verbose_name = "Shop Review"
        verbose_name_plural = "Shop Reviews"
        unique_together = ('shop', 'customer')

    def __str__(self):
        return f"{self.customer.user.username} -> {self.shop.name} ({self.rating}★)"
    

