from django.conf import settings
from django.db import models
from accounts.models import ShopOwnerProfile
    
#################################################### 
# Permission and Menu models (Will stay in admin_db)
#################################################### 
class MenuList(models.Model):
    module_name        = models.CharField(max_length=100, db_index=True)
    menu_name          = models.CharField(max_length=100, unique=True, db_index=True)
    menu_url           = models.CharField(max_length=250, unique=True)
    menu_icon          = models.CharField(max_length=250, blank=True, null=True)
    parent_id          = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_main_menu       = models.BooleanField(default=False)
    is_sub_menu        = models.BooleanField(default=False)
    is_sub_child_menu  = models.BooleanField(default=False)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)
    deleted_at         = models.DateTimeField(blank=True, null=True)
    created_by         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='menu_created_by')
    is_active          = models.BooleanField(default=True)
    deleted            = models.BooleanField(default=False)
    class Meta:
        db_table = "menu_list"
        verbose_name = "Menu List"
    def __str__(self) -> str:
        return f"{self.module_name} > {self.menu_name}"

class UserPermission(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_permissions_list") 
    menu        = models.ForeignKey(MenuList, on_delete=models.CASCADE, related_name="menu_permissions") 
    can_view    = models.BooleanField(default=False)
    can_add     = models.BooleanField(default=False)
    can_update  = models.BooleanField(default=False)
    can_delete  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="permission_created_by") 
    updated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="permission_updated_by", blank=True, null=True) 
    deleted_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="permission_deleted_by", blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    deleted     = models.BooleanField(default=False)
    class Meta:
        db_table = "user_permission"
    def __str__(self):
        return f"{self.user.username} - {self.menu.menu_name}"

class StaffRole(models.Model):
    shop_owner = models.ForeignKey(ShopOwnerProfile, on_delete=models.CASCADE, related_name='shop_roles')
    role_name = models.CharField(max_length=50) 
    permissions = models.ManyToManyField('MenuList')
    class Meta:
        db_table = 'staff_roles'
        unique_together = ('shop_owner', 'role_name')
    def __str__(self):
        return f"{self.role_name} ({self.shop_owner.shop_name})"

#################################################### 
# management site 
#################################################### 
class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255) 
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser_info = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'activity_logs'
    def __str__(self):
        return f"{self.user.username} - {self.action}"

class AdminNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'admin_notifications'
    def __str__(self):
        return self.title

class SystemSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Rabbi Mart')
    site_logo = models.ImageField(upload_to='settings/', null=True, blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    currency_symbol = models.CharField(max_length=10, default='৳')
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'system_settings'
    def __str__(self):
        return self.site_name