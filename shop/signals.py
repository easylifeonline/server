# # signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Product
# from .tasks import update_new_arrival_status
# from datetime import timedelta
# from django.utils import timezone

# @receiver(post_save, sender=Product)
# def set_new_arrival(sender, instance, created, **kwargs):
#     if created:
#         # Schedule the task to run 10 days later
#         update_new_arrival_status.apply_async((instance.id,), eta=timezone.now() + timedelta(days=10))