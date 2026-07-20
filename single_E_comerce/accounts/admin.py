from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import ShopOwnerProfile, CustomerProfile, EmailOTP

User = get_user_model()

# ১. কাস্টম ইউজার অ্যাডমিন (Security logic ঠিক রাখার জন্য)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display    = ('username', 'email', 'first_name', 'last_name', 'is_shop_owner', 'is_customer', 'is_staff')
    list_filter     = ('is_shop_owner', 'is_customer', 'is_staff', 'is_superuser', 'is_active')
    fieldsets       = UserAdmin.fieldsets + (
        ('User Roles', {'fields': ('is_shop_owner', 'is_customer')}),
    )
    add_fieldsets   = UserAdmin.add_fieldsets + (
        ('User Roles', {'fields': ('is_shop_owner', 'is_customer')}),
    )
    list_editable   = ('is_shop_owner', 'is_customer', 'is_staff')
    search_fields   = ('username', 'email', 'first_name', 'last_name')
# ২. শপ ওনার প্রোফাইল অ্যাডমিন
@admin.register(ShopOwnerProfile)
class ShopOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'nid_number', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active', 'district')
    search_fields = ('user__username', 'user__email', 'phone', 'nid_number')
    list_editable = ('is_verified', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Info', {
            'fields': ('user', 'phone', 'profile_pic')
        }),
        ('Verification & Legal', {
            'fields': ('trade_license', 'nid_number', 'is_verified', 'is_active')
        }),
        ('Location', {
            'fields': ('district', 'thana', 'address_details')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(CustomerProfile)
class CustomerProfile(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_verified', 'is_active')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('is_verified', 'is_active')

# ৪. ইমেইল ওটিপি অ্যাডমিন
@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'is_active')
    readonly_fields = ('created_at',)
    search_fields = ('email',)