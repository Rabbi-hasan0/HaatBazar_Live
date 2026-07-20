from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Shop, ShopSubscription, SubscriptionPlan
from datetime import date, timedelta

@receiver(post_save, sender=Shop)
def assign_free_plan(sender, instance, created, **kwargs):
    if created:
        free_plan = SubscriptionPlan.objects.filter(name='free').first()
        if free_plan:
            ShopSubscription.objects.create(
                shop=instance,
                plan=free_plan,
                expire_date=date.today() + timedelta(days=free_plan.duration_days)
            )
            