from django.contrib import admin
from .models import CustomUser, Product, Order, Review, Contact, Subscriber, Category, ProductCategory, ProductImage, ProductAttribute, Address, Inventory
from django.contrib.auth.admin import UserAdmin
from django.db import transaction, IntegrityError

import logging
logger = logging.getLogger(__name__)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone_number', 'address')
    list_filter = ('role',)
    search_fields = ('username', 'email')

    def save_model(self, request, obj, form, change):
        if change:
            original = CustomUser.objects.get(pk=obj.pk)
            if original.role != obj.role:
                try:
                    with transaction.atomic():
                        self.handle_role_change(obj, original.role, obj.role)
                except IntegrityError as e:
                    self.message_user(request, f"Error changing role: {e}", level='error')
                    return
        super().save_model(request, obj, form, change)

    def handle_role_change(self, user, old_role, new_role):
        if old_role == 'vendor' and new_role != 'vendor':
            self.deactivate_vendor_data(user)
        elif old_role == 'customer' and new_role == 'vendor':
            self.prepare_user_for_vendor(user)
        # Handle other role transitions if needed

    def deactivate_vendor_data(self, user):
        # Example: Deactivate or handle products related to the vendor
        products = Product.objects.filter(vendor=user)
        for product in products:
            product.active = False  # Assuming 'active' is a field to deactivate products
            product.save()

        # Alternatively, handle related orders if applicable
        orders = Order.objects.filter(user=user)
        for order in orders:
            order.status = 'Cancelled'  # Example action to cancel orders
            order.save()

    def prepare_user_for_vendor(self, user):
        # Example: Prepare a user to become a vendor, if necessary
        # This might include initializing vendor-specific settings or data
        pass

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Contact)
admin.site.register(Subscriber)
admin.site.register(Category)
admin.site.register(ProductCategory)
admin.site.register(ProductImage)
admin.site.register(ProductAttribute)
admin.site.register(Address)
admin.site.register(Inventory)

