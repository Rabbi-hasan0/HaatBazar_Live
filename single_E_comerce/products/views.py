from django.db import transaction
from django.urls import reverse
from django.contrib import messages
from django.db.models import Avg
from django.db.models import Q, Count, ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import ProductMainCategory, ProductSubCategory, Product, InventoryActivityLog, ProductReview
from ecomapp.views import paginate_data
from accounts.models import ShopOwnerProfile
from shops.models import Shop
from decimal import Decimal

@login_required
def main_category_list(request):
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('product_list')
        
    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
    
    if not user_shop:
        messages.error(request, "Active shop not found for your profile.")
        return redirect('product_list')
    
    qs = ProductMainCategory.objects.filter(shop=user_shop, is_active=True).annotate(product_count=Count('products')).order_by('-created_at')
    if search_query:
        qs = qs.filter(Q(main_cat_name__icontains=search_query) | Q(description__icontains=search_query)).distinct()
        
    ordered_qs = qs.order_by('-created_at', '-updated_at')
    data_list, paginator_list, last_page = paginate_data(request, page_number, ordered_qs)
    
    context = {
        'shop': user_shop,
        'page_title': "Main Category",
        'type': 'main_cat',
        'items': data_list,
        'product_main_categories': data_list,
        'paginator_list': paginator_list,
        'last_page': last_page,
        'query': search_query,
    }
    return render(request, 'products/main_cat/main_category_list.html', context)

@login_required
@transaction.atomic
def main_category_add(request):
    if request.method == 'POST':
        main_cat_name = request.POST.get('main_cat_name')
        cat_slug = request.POST.get('cat_slug', '') 
        description = request.POST.get('description')
        cat_image = request.FILES.get('cat_image') 
        
        try:
            user_profile = request.user.shop_owner_profile
        except ShopOwnerProfile.DoesNotExist:
            messages.error(request, "You do not have a shop owner profile.")
            return redirect('product_list')
            
        user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
    
        if not user_shop:
            messages.error(request, "Active shop not found for your profile.")
            return redirect('product_list')
        
        ProductMainCategory.objects.create(
            shop=user_shop,
            main_cat_name=main_cat_name,
            cat_slug=cat_slug,
            description=description,
            cat_image=cat_image, 
            created_by=user_profile
        )
        InventoryActivityLog.objects.create(
            shop=user_shop,
            module_type='main_cat',
            item_name=main_cat_name,
            action_type='add',
            performed_by=user_profile,
            details=f"New system root entry initialized for Main Category: '{main_cat_name}'"
        )
        messages.success(request, 'Category added successfully!')
        return redirect(request.META.get('HTTP_REFERER', 'main_category_list')) 
    return redirect('main_category_list') 

@login_required
@transaction.atomic
def main_category_edit(request, pk):
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('product_list')

    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
    category = get_object_or_404(ProductMainCategory, pk=pk, shop=user_shop)
    if request.method == 'POST':
        old_name = category.main_cat_name
        category.main_cat_name = request.POST.get('main_cat_name')
        category.description = request.POST.get('description')
        category.updated_by = request.user.shop_owner_profile
        if request.FILES.get('cat_image'):
            category.cat_image = request.FILES.get('cat_image')
        # Log text configuration engine
        details_str = f"Modified layout parameters."
        new_name = category.main_cat_name
        if old_name != new_name:
            details_str = f"Name mutated from '{old_name}' to '{new_name}'."
        InventoryActivityLog.objects.create(
            shop=user_shop,
            module_type='main_cat',
            item_name=new_name,
            action_type='edit',
            performed_by=user_profile,
            details=details_str
        )
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect(request.META.get('HTTP_REFERER', 'main_category_list'))
    return redirect('main_category_list')

@login_required
def main_category_delete(request, pk):
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('product_list')

    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
    category = get_object_or_404(ProductMainCategory, pk=pk, shop=user_shop)
    if category.products.exists(): 
        messages.error(request, f'Cannot delete "{category.main_cat_name}" because it contains products!')
        return redirect(request.META.get('HTTP_REFERER', 'main_category_list'))
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect(request.META.get('HTTP_REFERER', 'main_category_list'))
    return redirect('main_category_list')

@login_required
def sub_category_list(request):
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    selected_main_cats = request.GET.getlist('main_cats')
    
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('product_list')

    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()

    qs = ProductSubCategory.objects.filter(shop=user_shop, is_active=True).select_related('main_category').annotate(product_count=Count('products')).order_by('-created_at')
    if selected_main_cats:
        qs = qs.filter(main_category_id__in=selected_main_cats)
    if search_query:
        qs = qs.filter(
            Q(sub_cat_name__icontains=search_query) | 
            Q(main_category__main_cat_name__icontains=search_query)
        ).distinct()
        
    ordered_qs = qs.order_by('-created_at', '-updated_at')
    data_list, paginator_list, last_page = paginate_data(request, page_number, ordered_qs)
    
    product_main_categories = ProductMainCategory.objects.filter(shop=user_shop, is_active=True)
    
    context = {
        'shop': user_shop,
        'page_title': "Sub Category",
        'type': 'sub_cat',
        'items': data_list,
        'product_sub_categories': data_list,
        'product_main_categories': product_main_categories,
        'selected_main_cats': selected_main_cats,
        'paginator_list': paginator_list,
        'last_page': last_page,
        'query': search_query
    }
    return render(request, 'products/sub_category_list.html', context)

@login_required
@transaction.atomic
def sub_category_add(request):
    if request.method == "POST":
        sub_cat_name = request.POST.get('sub_cat_name')
        main_cat_id = request.POST.get('main_category')
        sub_cat_image = request.FILES.get('sub_cat_image')
        description = request.POST.get('description') 

        try:
            user_profile = request.user.shop_owner_profile
        except ShopOwnerProfile.DoesNotExist:
            messages.error(request, "You do not have a shop owner profile.")
            return redirect('sub_category_list')

        user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()

        ProductSubCategory.objects.create(
            shop=user_shop,
            main_category_id=main_cat_id, 
            sub_cat_name=sub_cat_name,
            sub_cat_image=sub_cat_image,
            description=description,
            created_by=user_profile 
        )
        InventoryActivityLog.objects.create(
            shop=user_shop,
            module_type='sub_cat',
            item_name=sub_cat_name,
            action_type='add',
            performed_by=user_profile,
            details=f"Attached new sub category node under main cat ID: #{main_cat_id}."
        )
        messages.success(request, "Sub Category added successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'sub_category_list'))
    return redirect('sub_category_list')

@login_required 
@transaction.atomic
def sub_category_edit(request, pk):
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('sub_category_list')

    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
    sub_category = get_object_or_404(ProductSubCategory, id=pk, shop=user_shop)
    if request.method == "POST":
        old_name = sub_category.sub_cat_name
        sub_category.sub_cat_name = request.POST.get('sub_cat_name')
        sub_category.description = request.POST.get('description')
        sub_category.updated_by = user_profile
        main_cat_id = request.POST.get('main_category')
        if main_cat_id:
            sub_category.main_category_id = main_cat_id
        if request.FILES.get('sub_cat_image'):
            sub_category.sub_cat_image = request.FILES.get('sub_cat_image')
        
        # Log text configuration engine
        details_str = f"Modified layout parameters."
        new_name = sub_category.sub_cat_name
        if old_name != new_name:
            details_str = f"Name mutated from '{old_name}' to '{new_name}'."
        InventoryActivityLog.objects.create(
            shop=user_shop,
            module_type='sub_cat',
            item_name=new_name,
            action_type='edit',
            performed_by=user_profile,
            details=details_str
        )
        sub_category.save()
        messages.success(request, "Sub Category updated successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'sub_category_list')) 
    return redirect('sub_category_list')

@login_required
def sub_category_delete(request, pk):
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('sub_category_list')

    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
    sub_category = get_object_or_404(ProductSubCategory, id=pk, shop=user_shop)
    if sub_category.products.exists():
        messages.error(request, f'Cannot delete "{sub_category.sub_cat_name}" because it contains products!')
        return redirect(request.META.get('HTTP_REFERER', 'sub_category_list')) 
    if request.method == 'POST':
        sub_category.delete()
        messages.success(request, 'Sub Category deleted successfully.')
        return redirect(request.META.get('HTTP_REFERER', 'sub_category_list')) 
    return redirect('sub_category_list')

@login_required
def product_list(request):
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)
    sort_by = request.GET.get('sort')
    stock_status = request.GET.get('stock')
    selected_main_cats = request.GET.getlist('main_cats')
    selected_sub_cats = request.GET.getlist('sub_cats')
    user_shop = request.user.shop_owner_profile.shops.filter(is_active=True).first()
    
    qs = Product.objects.filter(shop=user_shop, is_active=True).select_related('main_category', 'sub_category').annotate(
        total_reviews=Count('reviews', filter=Q(reviews__is_active=True), distinct=True),
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
        total_wishlist=Count('wishlisted_by', distinct=True)
    )
    
    if search_query:
        qs = qs.filter(Q(product_name__icontains=search_query) | Q(description__icontains=search_query)).distinct()
    if selected_main_cats:
        qs = qs.filter(main_category_id__in=selected_main_cats)
    if selected_sub_cats:
        qs = qs.filter(sub_category_id__in=selected_sub_cats)
    if stock_status == 'low_stock':
        qs = qs.filter(stock__gt=0, stock__lte=5)
    elif stock_status == 'out_of_stock':
        qs = qs.filter(stock=0)

    if sort_by == 'price_low':
        ordered_qs = qs.order_by('price')
    elif sort_by == 'price_high':
        ordered_qs = qs.order_by('-price')
    else:
        ordered_qs = qs.order_by('-created_at', '-updated_at')

    data_list, paginator_list, last_page = paginate_data(request, page_number, ordered_qs)
    
    product_main_categories = ProductMainCategory.objects.filter(shop=user_shop, is_active=True)
    product_sub_categories = ProductSubCategory.objects.filter(shop=user_shop, is_active=True)
    
    context = {
        'shop': user_shop,
        'page_title': "Product List",
        'type': 'products',
        'items': data_list,
        'all_products': data_list,
        'product_main_categories': product_main_categories,
        'product_sub_categories': product_sub_categories,
        'selected_main_cats': selected_main_cats,
        'selected_sub_cats': selected_sub_cats,
        'paginator_list': paginator_list,
        'last_page': last_page,
        'query': search_query
    }
    return render(request, 'products/product_list.html', context)

@login_required
@transaction.atomic
def product_add(request):
    if request.method == "POST":
        p_name = request.POST.get('product_name')
        main_cat_id = request.POST.get('main_category')
        sub_cat_id = request.POST.get('sub_category')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        image = request.FILES.get('product_image')
        
        try:
            user_profile = request.user.shop_owner_profile
        except ShopOwnerProfile.DoesNotExist:
            messages.error(request, "You do not have a shop owner profile.")
            return redirect('product_list')
            
        user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
        
        if not user_shop:
            messages.error(request, "Active shop not found for your profile.")
            return redirect('product_list')
            
        if not p_name or not main_cat_id or not price or not stock:
            messages.error(request, "Please fill up all the required fields.")
            return redirect(request.META.get('HTTP_REFERER', 'product_list'))

        Product.objects.create(
            shop=user_shop,
            product_name=p_name.strip(),
            main_category_id=int(main_cat_id),
            sub_category_id=int(sub_cat_id) if (sub_cat_id and sub_cat_id.isdigit()) else None,
            price=price,
            stock=stock,
            description=description,
            product_image=image,
            created_by=user_profile
        )
        
        messages.success(request, "Product added successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'product_list')) 
        
    return redirect('product_list')

@login_required
@transaction.atomic
def product_edit(request, id):
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('product_list')
        
    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()
    
    if not user_shop:
        messages.error(request, "Active shop not found for your profile.")
        return redirect('product_list')
    
    product = get_object_or_404(Product, id=id, shop=user_shop)
    if request.method == "POST":
        # পুরোনো ভ্যালুগুলো ট্র্যাকিংয়ের জন্য সংরক্ষণ
        old_name = product.product_name
        old_price = product.price
        old_stock = product.stock
        old_discount_pct = product.discount_percentage or 0  # নাল (Null) হ্যান্ডেল করার জন্য ০

        # পোস্ট ডাটা রিসিভ
        product.product_name = request.POST.get('product_name')
        new_name = product.product_name
        
        product.main_category_id = request.POST.get('main_category')
        product.sub_category_id = request.POST.get('sub_category') or None
        
        product.price = request.POST.get('price')
        new_price = product.price
        
        product.stock = request.POST.get('stock')
        new_stock = product.stock
        
        product.description = request.POST.get('description')
        product.updated_by = request.user.shop_owner_profile
        
        if request.FILES.get('product_image'):
            product.product_image = request.FILES.get('product_image')
        
        # --- ডিসকাউন্ট পার্সেন্টেজ এবং ডিসকাউন্ট প্রাইস ক্যালকুলেশন ---
        discount_pct_input = request.POST.get('discount_percentage')
        
        if discount_pct_input and int(discount_pct_input) > 0:
            new_discount_pct = int(discount_pct_input)
            product.discount_percentage = new_discount_pct
            
            # সূত্র: discount_price = price - (price * pct / 100)
            current_price_decimal = Decimal(str(product.price))
            discount_amount = current_price_decimal * Decimal(new_discount_pct / 100)
            product.discount_price = current_price_decimal - discount_amount
        else:
            new_discount_pct = 0
            product.discount_percentage = 0
            product.discount_price = None
        # ------------------------------------------------------------

        # চেঞ্জেস বা অ্যাক্টিভিটি লগ ট্র্যাকিং
        changes = []
        if old_name != new_name: 
            changes.append(f"Name change ({old_name} → {new_name})")
        if float(old_price) != float(new_price): 
            changes.append(f"Price adjusted (${old_price} → ${new_price})")
        if int(old_stock) != int(new_stock): 
            changes.append(f"Stock mutated ({old_stock} → {new_stock} units)")
        if old_discount_pct != new_discount_pct: 
            changes.append(f"Discount mutated ({old_discount_pct}% → {new_discount_pct}%)")
        
        # অ্যাক্টিভিটি লগ তৈরি
        InventoryActivityLog.objects.create(
            shop=user_shop,
            module_type='product',
            item_name=product.product_name,
            action_type='edit',
            performed_by=user_profile,
            details=", ".join(changes) if changes else "Meta schema specifications processed."
        )
        
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'product_list')) 
        
    return redirect('product_list')

@login_required
def product_delete(request, id):
    try:
        user_profile = request.user.shop_owner_profile
    except ShopOwnerProfile.DoesNotExist:
        messages.error(request, "You do not have a shop owner profile.")
        return redirect('product_list')

    user_shop = Shop.objects.filter(owner=user_profile, is_active=True).first()

    if not user_shop:
        messages.error(request, "Active shop not found for your profile.")
        return redirect('product_list')

    product = get_object_or_404(Product, id=id, shop=user_shop)
    if request.method == 'POST':
        try:
            p_name = product.product_name
            product.delete()
            messages.success(request, f'Product "{p_name}" deleted successfully!')
        except ProtectedError:
            messages.warning(request, f'"{product.product_name}" cannot be deleted (it has orders)')
        return redirect(request.META.get('HTTP_REFERER', 'product_list')) 
    return redirect('product_list')

def product_bulk_delete(request):
    if request.method == 'POST':
        selected_ids_str = request.POST.get('selected_ids', '')
        if selected_ids_str:
            id_list = [int(x) for x in selected_ids_str.split(',') if x.isdigit()]
            deleted_count, _ = Product.objects.filter(id__in=id_list).delete()
            messages.success(request, f'Successfully purged {deleted_count} product entries.')
        else:
            messages.error(request, 'No products selected.')
    return redirect('product_list')

@login_required
def activity_log_list(request):
    page_number = request.GET.get('page', 1)
    module_filter = request.GET.get('module', '').strip()
    action_filter = request.GET.get('action', '').strip()
    user_shop = request.user.shop_owner_profile.shops.filter(is_active=True).first()
    qs = InventoryActivityLog.objects.filter(shop=user_shop).select_related('performed_by__user')
    if module_filter:
        qs = qs.filter(module_type=module_filter)
    if action_filter:
        qs = qs.filter(action_type=action_filter)
    ordered_qs = qs.order_by('-created_at')
    data_list, paginator_list, last_page = paginate_data(request, page_number, ordered_qs)
    context = {
        'shop': user_shop,
        'page_title': "Inventory Activity Audit Log",
        'logs': data_list,
        'paginator_list': paginator_list,
        'last_page': last_page,
        'current_module': module_filter,
        'current_action': action_filter,
    }
    return render(request, 'products/activity_logs.html', context)

