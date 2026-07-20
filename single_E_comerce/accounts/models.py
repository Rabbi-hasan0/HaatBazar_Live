from django.contrib.auth.models import AbstractUser
from admin_management.utils import generate_unique_slug
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
#################################################### 
# Admin Profile and Auth (Will stay in admin_db)
#################################################### 

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_shop_owner = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)

class ShopOwnerProfile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop_owner_profile', db_index=True, unique=True, limit_choices_to={'is_shop_owner': True})
    phone           = models.CharField(max_length=15, db_index=True)
    profile_pic     = models.ImageField(upload_to='admin_pics/', null=True, blank=True)
    trade_license   = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    nid_number      = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    date_of_birth   = models.DateField(null=True, blank=True)
    gender          = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    district        = models.CharField(max_length=50, null=True, blank=True)
    thana           = models.CharField(max_length=50, null=True, blank=True)
    address_details = models.CharField(max_length=255, null=True, blank=True)
    is_active       = models.BooleanField(default=True, db_index=True)
    is_verified     = models.BooleanField(default=False, db_index=True,) 
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='shop_owner_created_by', null=True, blank=True)
    updated_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='shop_owner_updated_by', null=True, blank=True)
    verified_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='verified_shops_by', null=True, blank=True)
    class Meta:
        db_table = 'shop_owners'
        verbose_name = "Shop Owner"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    # def __str__(self):
    #     return f"Shop Owner- ({self.user.username})"
    def __str__(self):
        try:
            if self.user:
                return f"Shop Owner- ({self.user.username})"
        except User.DoesNotExist:
            return f"Shop Owner- (Deleted User, ID: {self.id})"
        
        return f"Shop Owner- (No User)"

class CustomerProfile(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone         = models.CharField(max_length=15, db_index=True)
    profile_pic   = models.ImageField(upload_to='customer_pics/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender        = models.CharField(max_length=10, null=True, blank=True)
    district      = models.CharField(max_length=50, null=True, blank=True)
    thana         = models.CharField(max_length=50, null=True, blank=True)
    address_details= models.CharField(max_length=255, null=True, blank=True)
    is_verified   = models.BooleanField(default=False, db_index=True)
    is_active     = models.BooleanField(default=False, db_index=True)
    updated_at    = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'customers'  
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created: 
        if instance.is_shop_owner:
            ShopOwnerProfile.objects.get_or_create(user=instance)
        if instance.is_customer:
            CustomerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_shop_owner and hasattr(instance, 'shop_owner_profile'):
        instance.shop_owner_profile.save()
    if instance.is_customer and hasattr(instance, 'customer_profile'):
        instance.customer_profile.save()

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_sessions'

class EmailOTP(models.Model):
    email      = models.EmailField(db_index=True)
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)
    class Meta:
        db_table = 'email_otps'
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)
    def __str__(self):
        return f"{self.email} - {self.code}"
