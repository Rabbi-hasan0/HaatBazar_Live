from admin_management.models import UserPermission
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages

def checkUserPermission(request, access_type, menu_url):
    try:
        user_permissions = {
            "can_view": "can_view",
            "can_add": "can_add",
            "can_update": "can_update",
            "can_delete": "can_delete",
        }

        if request.user.is_superuser: return True

        check_user_permission = UserPermission.objects.filter(
            user_id=request.user.id, is_active=True, **{user_permissions[access_type]: True}, menu__menu_url=menu_url,
        )
 
        if check_user_permission: return True
        else: return False
    except:
        return False

