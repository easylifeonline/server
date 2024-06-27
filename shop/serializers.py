from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from shop.document import ProductDocument
from .models import (
    ClickedProduct, CustomUser, Address, Order, 
    SearchQuery, Subscriber, VendorRequest, Visit
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
    class Meta:
        model = Category
        fields = ['id', 'name']

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

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'category_id', 'image', 'sku']

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.category = validated_data.get('category', instance.category)
        instance.sku = validated_data.get('sku', instance.sku)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'total', 'created_at', 'items']


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
