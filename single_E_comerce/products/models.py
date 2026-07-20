from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db import models
from django.utils import timezone
from accounts.models import ShopOwnerProfile
from single_E_comerce import settings
    
class ProductMainCategory(models.Model):
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='main_categories', db_index=True)
    main_cat_name = models.CharField(max_length=100)
    cat_slug = models.SlugField(max_length=150, blank=True)
    cat_image = models.ImageField(upload_to='ecommerce/category_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cat_ordering = models.IntegerField(default=0, blank=True, null=True)
    created_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='category_created_by')
    updated_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='category_updated_by', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_category'
        verbose_name_plural = 'Product Categories'
        unique_together = ('shop', 'cat_slug')
        ordering = ['-is_active', 'cat_ordering']

    def __str__(self):
        return f"{self.shop.shop_name} - {self.main_cat_name}"
    
    def save(self, *args, **kwargs):
        if not self.cat_slug and self.main_cat_name:
            base_slug = slugify(self.main_cat_name)
            slug = base_slug
            num = 1
            while ProductMainCategory.objects.filter(shop=self.shop, cat_slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.cat_slug = slug
        super().save(*args, **kwargs)
    
class ProductSubCategory(models.Model):
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='sub_categories', db_index=True)
    main_category = models.ForeignKey(ProductMainCategory, on_delete=models.CASCADE, related_name='sub_categories')
    sub_cat_name = models.CharField(max_length=100)
    sub_cat_slug = models.SlugField(max_length=150, blank=True)
    sub_cat_image = models.ImageField(upload_to='ecommerce/sub_category_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sub_cat_ordering = models.IntegerField(default=0)
    created_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='sub_category_created_by')
    updated_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='sub_category_updated_by', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_sub_category'
        verbose_name_plural = 'Product Sub Categories'
        unique_together = ('shop', 'sub_cat_slug')
        ordering = ['-is_active', 'sub_cat_ordering']

    def __str__(self):
        return f"{self.main_category.main_cat_name} -> {self.sub_cat_name}"
    
    def save(self, *args, **kwargs):
        if not self.sub_cat_slug and self.sub_cat_name:
            base_slug = slugify(self.sub_cat_name)
            slug = base_slug
            num = 1
            while ProductSubCategory.objects.filter(shop=self.shop, sub_cat_slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.sub_cat_slug = slug
        super().save(*args, **kwargs)
    
class Product(models.Model):
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='products', db_index=True)
    product_name = models.CharField(max_length=100, db_index=True)
    product_slug = models.SlugField(max_length=150, blank=True)
    product_image = models.ImageField(upload_to='ecommerce/product_images/', blank=True, null=True)
    main_category = models.ForeignKey(ProductMainCategory, on_delete=models.CASCADE, related_name='products')
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    total_views = models.PositiveIntegerField(default=0)
    discount_percentage = models.PositiveIntegerField(default=0, blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='product_created_by')
    updated_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='product_updated_by', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products'
        verbose_name_plural = 'Products'
        unique_together = ('shop', 'product_slug')
        ordering = ['-is_active']

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        if not self.product_slug and self.product_name:
            base_slug = slugify(self.product_name)
            slug = base_slug
            num = 1
            while Product.objects.filter(shop=self.shop, product_slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.product_slug = slug
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        return self.reviews.filter(is_active=True).aggregate(models.Avg('rating'))['rating__avg'] or 0

class InventoryActivityLog(models.Model):
    MODULE_CHOICES = (
        ('main_cat', 'Main Category'),
        ('sub_cat', 'Sub Category'),
        ('product', 'Product Base Matrix'),
    )
    ACTION_CHOICES = (
        ('add', 'Created'),
        ('edit', 'Updated/Mutated'),
        ('delete', 'Deleted/Purged'),
    )
    
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='inventory_activity_logs', db_index=True)
    module_type = models.CharField(max_length=15, choices=MODULE_CHOICES, db_index=True)
    item_name = models.CharField(max_length=255) # Category ba Product er nam save thakbe
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, db_index=True)
    performed_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True, null=True) # Ki change hoilo tar specific description
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'inventory_activity_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_module_type_display()}] {self.item_name} ({self.action_type})"

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist', db_index=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='wishlisted_by', db_index=True)
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_wishlist'
        unique_together = ('user', 'product') 

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"
    
class ProductReview(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews', db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, db_index=True) 
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating should be between 1 to 5"
    )
    comment = models.TextField(blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True) 
    created_by = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='product_review_created_by', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'product_reviews'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.product.product_name} - {self.rating} Star"
 
class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    )
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='shop_events', db_index=True)
    title = models.CharField(max_length=255, verbose_name="Event Title")
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    banner_desktop = models.ImageField(upload_to='events/desktop/')
    banner_mobile = models.ImageField(upload_to='events/mobile/', null=True, blank=True)
    product = models.ManyToManyField(Product, related_name='events', blank=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('shop', 'slug')
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Event.objects.filter(shop=self.shop, slug=slug).exclude(pk=self.pk).exists():
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