from django.shortcuts import render
from django.db.models import Avg, Count
from shops.models import Shop, ShopReview

def home_page_view(request):
    search_query = request.GET.get('shop_search', '').strip()
    
    if search_query:
        shops_queryset = Shop.objects.filter(
            is_active=True,
            shop_name__icontains=search_query
        )
    else:
        shops_queryset = Shop.objects.filter(is_active=True).order_by('-created_at')
        
    shops_with_ratings = shops_queryset.annotate(
        avg_rating=Avg('reviews__rating'),     
        total_reviews=Count('reviews')
    )

    recent_reviews = ShopReview.objects.filter(is_visible=True).select_related('customer__user').order_by('-created_at')[:3]

    context = {
        'shop_first_half': 'Haat',        
        'shop_second_half': 'Bazar',
        'shops': shops_with_ratings,
        'recent_reviews': recent_reviews,
        'search_query': search_query,     
    }

    return render(request, 'haatbazar/home.html', context)