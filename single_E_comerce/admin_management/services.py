import pandas as pd
from django.core.exceptions import ValidationError
from products.models import Product, ProductMainCategory

def bulk_upload_products(file, shop):
    # ১. সাবস্ক্রিপশন লিমিট চেক করা
    current_product_count = Product.objects.filter(shop=shop).count()
    plan_limit = shop.current_subscription.plan.product_limit

    df = pd.read_excel(file)
    upload_count = len(df)

    if current_product_count + upload_count > plan_limit:
        raise ValidationError(f"আপনার প্ল্যান অনুযায়ী আপনি সর্বোচ্চ {plan_limit}টি প্রোডাক্ট রাখতে পারেন।")

    # ২. ডেটা প্রসেসিং
    product_list = []
    for index, row in df.iterrows():
        # ক্যাটাগরি ম্যানেজমেন্ট
        category, _ = ProductMainCategory.objects.get_or_create(
            shop=shop,
            main_cat_name=row['category'],
            defaults={'created_by': shop.owner}
        )

        # প্রোডাক্ট অবজেক্ট তৈরি (সেভ না করে লিস্টে রাখা - Fast processing)
        product_list.append(Product(
            shop=shop,
            product_name=row['product_name'],
            main_category=category,
            price=row['price'],
            stock=row.get('stock', 0),
            created_by=shop.owner
        ))

    # ৩. Bulk Create (একসাথে সব সেভ হবে, ডাটাবেসে প্রেসার কম পড়বে)
    Product.objects.bulk_create(product_list)
    return upload_count