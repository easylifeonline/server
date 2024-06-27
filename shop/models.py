from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='customer')
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.username

    def change_role(self, new_role):
        old_role = self.role
        if old_role != new_role:
            self.role = new_role
            self.save()
            if old_role == 'vendor' and new_role != 'vendor':
                self.deactivate_vendor_data()
            elif old_role == 'customer' and new_role == 'vendor':
                self.prepare_user_for_vendor()

    def deactivate_vendor_data(self):
        # Example: Deactivate or handle products related to the vendor
        products = Product.objects.filter(vendor=self)
        for product in products:
            product.active = False  # Assuming 'active' is a field to deactivate products
            product.save()

    def prepare_user_for_vendor(self):
        # Example: Prepare a user to become a vendor, if necessary
        pass

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    street_name = models.CharField(max_length=255)
    house_number = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_name}, {self.house_number}, {self.city}, {self.state}, {self.country}"

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
     
class Product(models.Model):
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True) 

    def __str__(self):
        return self.title

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField('Product')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review {self.id} for {self.product.name} by {self.user.username}'

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Contact {self.id} from {self.name}'

class Subscriber(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.name} in {self.category.name}'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f'Image {self.id} of {self.product.name}'

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}: {self.value} for {self.product.name}'

    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=255)
    variant_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.variant_name}: {self.variant_value}"

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.title} - {self.quantity} in stock"
    

class Visit(models.Model):
    count = models.PositiveIntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True)

class ClickedProduct(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.title} clicked {self.count} times'

class SearchQuery(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query
    
class VendorRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    ACTIVITY_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    ]

    business_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    product_types = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='actif')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
