from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import (
    Cart, CartItem, ClickedProduct, ContactSubmission, CustomUser, Address, HelpArticle, HelpCategory, Order, OrderItem, ProductDatabase, 
    SearchQuery, Subscriber, VendorPoliciesGuidelines, VendorRequest, Visit
)
from .models import Product, ProductImage
from .models import ProductVariant, Category, Inventory


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street_name', 'house_number', 'zip_code', 'city', 'state', 'country']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture', 'email', 'role']

    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance
    

class ProductDocumentSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    sku = serializers.CharField()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']
    

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'subcategories']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'variant_name', 'variant_value']

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title', read_only=True)  # Include the product title
    product_id = serializers.IntegerField(source='product.id', read_only=True)  # Include the product ID

    class Meta:
        model = Inventory
        fields = ['id', 'quantity', 'product_id', 'product_name']


# class ProductSerializer(serializers.ModelSerializer):
#     variants = ProductVariantSerializer(many=True, read_only=True)
#     inventory = InventorySerializer(many=True, read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
#     category = CategorySerializer(read_only=True)

#     class Meta:
#         model = Product
#         fields = ['id', 'title', 'description', 'price', 'category', 'category_id', 'image', 'sku', 'variants', 'inventory']

#     def create(self, validated_data):
#         category = validated_data.pop('category')
#         product = Product.objects.create(category=category, **validated_data)
#         return product

class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'category', 'category_id', 'sku', 
            'created_at', 'updated_at', 'is_best_seller', 'is_new_arrival', 
            'views', 'active', 'images', 'uploaded_images'
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = super().create(validated_data)
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', None)
        product = super().update(instance, validated_data)
        if uploaded_images:
            for image in uploaded_images:
                ProductImage.objects.create(product=product, image=image)
        return product
    
class ProductDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDatabase
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['email']

    def validate_email(self, value):
        if Subscriber.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return value
    

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = '__all__'

class ClickedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClickedProduct
        fields = '__all__'

class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = '__all__'

class VendorRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorRequest
        fields = [
            'id',
            'business_name',
            'contact_person',
            'email',
            'phone',
            'product_types',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
            'description',
            'status',
            'activity',
            'created_at'
        ]

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price', 'image']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'billing_address', 'shipping_address', 'status', 'payment_method', 'total', 'items']


class HelpCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpCategory
        fields = ['id', 'name', 'description']


class HelpArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpArticle
        fields = ['id', 'category', 'title', 'content', 'views']


class VendorPoliciesGuidelinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPoliciesGuidelines
        fields = ['id', 'title', 'description']


class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = '__all__'