from django.core.management.base import BaseCommand
from shop.models import Product, Category, Inventory
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Add dummy products to the database'

    def handle(self, *args, **kwargs):
        # Create categories
        categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports']
        category_objects = []
        for name in categories:
            category, created = Category.objects.get_or_create(name=name)
            category_objects.append(category)

        # Get a vendor user (assuming there's one with username 'vendor')
        vendor = User.objects.filter(role='vendor').first()
        if not vendor:
            self.stdout.write(self.style.ERROR('No vendor user found. Create a vendor user first.'))
            return

        # Create dummy products
        products = [
            {'title': 'Smartphone', 'description': 'A high-end smartphone', 'price': 699.99, 'category': 'Electronics', 'sku': 'SP001'},
            {'title': 'Laptop', 'description': 'A powerful gaming laptop', 'price': 1299.99, 'category': 'Electronics', 'sku': 'LT001'},
            {'title': 'Novel', 'description': 'A best-selling novel', 'price': 19.99, 'category': 'Books', 'sku': 'BK001'},
            {'title': 'T-shirt', 'description': 'A comfortable cotton t-shirt', 'price': 14.99, 'category': 'Clothing', 'sku': 'CL001'},
            {'title': 'Vacuum Cleaner', 'description': 'A powerful vacuum cleaner', 'price': 199.99, 'category': 'Home', 'sku': 'HM001'},
            {'title': 'Running Shoes', 'description': 'Lightweight running shoes', 'price': 49.99, 'category': 'Sports', 'sku': 'SP002'}
        ]

        for product_data in products:
            category = next((cat for cat in category_objects if cat.name == product_data['category']), None)
            product = Product.objects.create(
                vendor=vendor,
                title=product_data['title'],
                description=product_data['description'],
                price=product_data['price'],
                category=category,
                sku=product_data['sku']
            )
            Inventory.objects.create(product=product, quantity=random.randint(10, 100))

        self.stdout.write(self.style.SUCCESS('Successfully added dummy products'))
