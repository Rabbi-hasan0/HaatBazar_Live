from django.contrib import admin
from .models import (
    MenuList, UserPermission, StaffRole, 
    ActivityLog, AdminNotification, SystemSettings
)

@admin.register(MenuList)
class MenuListAdmin(admin.ModelAdmin):
    # 'parent' এর বদলে 'parent_id' এবং 'menu_order' বাদ দিয়েছি কারণ মডেলে নেই
    list_display = ('menu_name', 'module_name', 'parent_id', 'is_active') 
    list_filter = ('module_name', 'is_active')
    search_fields = ('menu_name', 'module_name')
    # ordering থেকেও menu_order সরিয়ে দিয়েছি
    ordering = ('menu_name',) 

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu', 'can_view', 'can_add', 'can_update', 'can_delete', 'is_active')
    list_filter = ('is_active', 'user', 'menu')
    search_fields = ('user__username', 'menu__menu_name')
    list_editable = ('can_view', 'can_add', 'can_update', 'can_delete', 'is_active')

@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    # আপনার মডেলে 'shop' এবং 'is_active' নেই, তাই এগুলো বাদ দিয়েছি
    list_display = ('role_name',) 
    # list_filter থেকে এরর দেওয়া ফিল্ডগুলো সরিয়েছি
    list_filter = () 
    # যদি ManyToMany ফিল্ড থাকে তবেই এটা রাখবেন, নাহলে কমেন্ট করে দিন
    # filter_horizontal = ('permissions',) 

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    readonly_fields = ('user', 'action', 'ip_address', 'browser_info', 'created_at')

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone')