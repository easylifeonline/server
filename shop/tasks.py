# # tasks.py
# from celery import shared_task
# from django.utils import timezone
# from .models import Product

# @shared_task
# def update_new_arrival_status(product_id):
#     try:
#         product = Product.objects.get(id=product_id)
#         if product.is_new_arrival:
#             product.is_new_arrival = False
#             product.save()
#     except Product.DoesNotExist:
#         pass
