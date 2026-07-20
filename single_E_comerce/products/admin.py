from import_export import resources 
from django.utils.text import slugify
from django.contrib import admin
from django.utils.timezone import now
from import_export.admin import ImportExportModelAdmin
from products.models import Product, ProductMainCategory, ProductSubCategory, ProductReview, Wishlist
from accounts.models import ShopOwnerProfile

# --- ১. প্রোডাক্ট ইমপোর্ট-এক্সপোর্ট কনফিগারেশন (Resource) ---
class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = (
            'id', 'shop', 'product_name', 'product_slug', 
            'main_category', 'sub_category', 'price', 'stock', 
            'is_featured', 'discount_percentage', 'discount_price', 
            'description', 'created_by', 'is_active'
        )
        import_id_fields = ('id',)

    def before_import_row(self, row, **kwargs):
        # ১. স্লাগ অটো জেনারেট লজিক
        shop_id = row.get('shop')
        product_name = row.get('product_name')
        
        if ('product_slug' not in row or not row['product_slug']) and product_name:
            base_slug = slugify(product_name)
            slug = base_slug
            num = 1
            while Product.objects.filter(shop_id=shop_id, product_slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            row['product_slug'] = slug

        # ২. created_by ফিক্সিং (ভুল বা খালি ID দিলে ডিফল্ট প্রথম ShopOwnerProfile ধরে নেবে)
        created_by_id = row.get('created_by')
        if created_by_id:
            # এক্সেলে দেওয়া ID ডাটাবেজে আছে কিনা চেক করবে
            if not ShopOwnerProfile.objects.filter(id=created_by_id).exists():
                first_profile = ShopOwnerProfile.objects.first()
                if first_profile:
                    row['created_by'] = first_profile.id
        else:
            first_profile = ShopOwnerProfile.objects.first()
            if first_profile:
                row['created_by'] = first_profile.id
        
@admin.register(ProductMainCategory)
class ProductMainCategoryAdmin(admin.ModelAdmin):
    list_display         = ('main_cat_name', 'cat_slug', 'cat_ordering', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter          = ('is_active',)
    search_fields        = ('main_cat_name', 'cat_slug')
    ordering             = ('cat_ordering',) 

@admin.register(ProductSubCategory)
class ProductSubCategoryAdmin(admin.ModelAdmin):
    list_display         = ('sub_cat_name', 'main_category', 'sub_cat_ordering', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter          = ('is_active',)
    search_fields        = ('sub_cat_name', 'sub_cat_slug')
    ordering             = ('sub_cat_ordering',) 

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display         = ('product', 'user', 'rating', 'comment', 'created_at')
    list_filter          = ('product', 'user', 'rating')
    search_fields        = ('comment',)
    ordering             = ('created_at',) 

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display         = ('product', 'user', 'shop', 'created_at')
    list_filter          = ('product', 'user', 'shop')
    search_fields        = ('product__product_name',)
    ordering             = ('created_at',) 


# --- ৩. প্রোডাক্ট ইমপোর্ট-এক্সপোর্ট অ্যাডমিন ---
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin): # এখানে ImportExportModelAdmin ব্যবহার করা হয়েছে
    resource_class = ProductResource
    
    list_display = (
        'product_name', 'main_category', 'sub_category', 'price', 'stock', 
        'is_featured', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active'
    )
    list_editable = ('is_featured', 'is_active', 'stock') 
    list_filter = ('is_active', 'is_featured', 'main_category', 'sub_category')
    search_fields = ('product_name', 'main_category__main_cat_name', 'sub_category__sub_cat_name', 'product_slug')
    ordering = ('product_name',)