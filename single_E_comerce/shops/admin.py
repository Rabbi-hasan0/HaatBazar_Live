from django.contrib import admin
from .models import Shop, SubscriptionPlan, ShopSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'product_limit', 'order_limit', 'duration_days', 'is_active')
    list_editable = ('price', 'product_limit', 'order_limit', 'duration_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

class ShopSubscriptionInline(admin.StackedInline):
    model = ShopSubscription
    extra = 0
    can_delete = False
    readonly_fields = ('start_date',)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'shop_type', 'owner', 'shop_slug', 'currency', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'currency')
    search_fields = ('shop_name', 'shop_slug', 'owner__user__username', 'email')
    prepopulated_fields = {'shop_slug': ('shop_name',)}
    list_editable = ('is_active', 'shop_type', 'is_verified')
    inlines = [ShopSubscriptionInline] # শপ এডিট করার সময় নিচেই সাবস্ক্রিপশন দেখা যাবে
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'shop_name', 'shop_slug', 'shop_logo', 'shop_description', 'banner_image')
        }),
        ('Configuration', {
            'fields': ('currency', 'timezone', 'invoice_prefix')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'trade_license','shop_address')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified')
        }),
    )

@admin.register(ShopSubscription)
class ShopSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('shop', 'plan', 'start_date', 'expire_date', 'is_active')
    list_filter = ('plan', 'is_active', 'expire_date')
    search_fields = ('shop__shop_name', 'plan__name')
    
from .models import ShopActivityLog
@admin.register(ShopActivityLog)
class ShopActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'created_at')
    list_filter = ('shop', 'created_at')
    search_fields = ('shop__shop_name',)
    readonly_fields = ('shop', 'created_at')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    ordering = ['-created_at']