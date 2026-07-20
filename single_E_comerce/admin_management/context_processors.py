# from admin_management.models import MenuList, UserPermission
# from accounts.models import CustomerProfile
# from ecomapp.models import OrderCart
# from ecomapp.views import cart_amount_summary

# def menu_items(request):
#     menu_list             = UserPermission.objects.filter(user_id=request.user.id, menu__is_main_menu=True, can_view=True, menu__parent_id=0, menu__is_active=True, menu__deleted=False, is_active=True).select_related('menu','user')
#     search_menu_list      = UserPermission.objects.filter(user_id=request.user.id, can_view=True, menu__is_active=True, menu__deleted=False, is_active=True).select_related('menu','user')
#     # print(menu_list.query)
#     # print(search_menu_list.query)
#     return {'main_menu_list':  menu_list, 'search_menu_list': search_menu_list}


# def get_cart_item(request):
#     customer = None
#     cart_items = []
#     if request.user.is_authenticated:
#         customer = Customer.objects.filter(user=request.user).first()
#         cart_items = OrderCart.objects.filter(customer=customer, is_active=True, is_order=False)
    
#     # Amount summary views theke call hocche
#     amount_summary = cart_amount_summary(request)
#     return {
#         'customer': customer,           # Eta add kora holo
#         'cart_item_count': len(cart_items), 
#         'cart_items': cart_items, 
#         'amount_summary': amount_summary
#     }

# def setting_menu_processor(request):
#     return {
#         'get_setting_menu': MenuList.objects.filter(module_name='Setting', is_active=True)
#     }