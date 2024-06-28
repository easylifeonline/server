from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.db import models
import logging
from django.db.models import Sum
from django.contrib.auth import get_user_model
from elasticsearch_dsl.query import MultiMatch
from django.core.mail import send_mail
from elasticsearch_dsl import Search, Q
import requests
from django.views.decorators.csrf import csrf_exempt
from shop.document import ProductDocument
from django.http import JsonResponse
from .serializers import ClickedProductSerializer, OrderSerializer, RegisterSerializer, SearchQuerySerializer, SubscriberSerializer, UserProfileSerializer, AddressSerializer, VendorRequestSerializer, VisitSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django_elasticsearch_dsl.search import Search
from rest_framework.views import APIView
from rest_framework import viewsets
from django.http import HttpResponse
from rest_framework import status
from .models import Address, ClickedProduct, CustomUser, ProductImage, SearchQuery, Subscriber, VendorRequest, Visit
from rest_framework import generics, permissions
from django.contrib.auth import logout
from .models import Product, ProductVariant, Category, Inventory, Order
from .serializers import ProductSerializer, ProductVariantSerializer, CategorySerializer, InventorySerializer
from django.conf import settings

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def change_role(self, request, pk=None):
        user = self.get_object()
        role = request.data.get('role', None)
        if role and role in dict(CustomUser.ROLE_CHOICES):
            user.role = role
            user.save()
            return Response({'status': 'role updated'})
        else:
            return Response({'status': 'invalid role'}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture.url if user.profile_picture else None
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # For session-based logout
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'vendor':
            vendor = self.request.query_params.get('vendor', None)
            if vendor:
                return self.queryset.filter(vendor__username=vendor)
        return self.queryset.none()

    def perform_create(self, serializer):
        try:
            serializer.save(vendor=self.request.user)
            logger.info("Product created successfully.")
        except Exception as e:
            logger.error(f"Error during product creation: {str(e)}")
            raise e

    def perform_update(self, serializer):
        try:
            serializer.save()
            logger.info("Product updated successfully.")
        except Exception as e:
            logger.error(f"Error during product update: {str(e)}")
            raise e
    

class ProductViewAllSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class ProductSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            search = Search(index=ProductDocument.Index.name).query(
                Q("multi_match", query=query, fields=['title', 'description'])
            )
            response = search.execute()
            products = [hit.to_dict() for hit in response]
            return Response(products, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        This method is used to associate the user with the inventory upon creation.
        """
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to forcibly
            # invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=True, methods=['put', 'patch'])
    def update_inventory(self, request, pk=None):
        """
        Custom action for updating inventory, if needed.
        """
        inventory = self.get_object()
        serializer = self.get_serializer(inventory, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """
        This method is used to save the updates to the instance.
        """
        serializer.save(user=self.request.user)

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_users = CustomUser.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        data = {
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders
        }
        return Response(data)

logger = logging.getLogger(__name__)

class VendorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            vendor = request.user
            if vendor.role != 'vendor':
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

            # Calculate total sales for the vendor
            total_sales = Order.objects.filter(items__vendor=vendor).aggregate(Sum('total'))['total__sum'] or 0
            
            # Calculate total products for the vendor
            total_products = Product.objects.filter(vendor=vendor).count()
            
            # Calculate pending orders for the vendor
            pending_orders = Order.objects.filter(items__vendor=vendor, status='pending').distinct().count()

            data = {
                'total_sales': total_sales,
                'total_products': total_products,
                'pending_orders': pending_orders
            }
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching vendor dashboard data: {e}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user
        orders = Order.objects.filter(user=customer)
        orders_data = OrderSerializer(orders, many=True).data
        data = {
            'orders': orders_data
        }
        return Response(data)
    

class SubscriberCreateView(generics.CreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    permission_classes = [AllowAny]


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer

    def create(self, request, *args, **kwargs):
        visit, created = Visit.objects.get_or_create(id=1)
        visit.count += 1
        visit.save()
        return Response({'count': visit.count, 'last_visit': visit.last_visit})

class ClickedProductView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        clicked_products = ClickedProduct.objects.select_related('product').all()
        serializer = ClickedProductSerializer(clicked_products, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
            user = request.user if request.user.is_authenticated else None
            clicked_product, created = ClickedProduct.objects.get_or_create(
                product=product,
                user=user,
                defaults={'count': 1}
            )
            if not created:
                clicked_product.count = models.F('count') + 1
                clicked_product.save(update_fields=['count'])
                clicked_product.refresh_from_db()
            return Response({"message": "Product click tracked successfully.", "click_count": clicked_product.count}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchQueryView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        query = request.data.get('query')

        SearchQuery.objects.create(user=user, query=query)
        return Response({"message": "Search query tracked successfully."}, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


@csrf_exempt
def proxy_elasticsearch(request, path):
    url = f"http://localhost:9200/{path}"
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.GET)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, data=request.body)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, data=request.body)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)

        return JsonResponse(response.json(), status=response.status_code, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    

class VendorRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = VendorRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = VendorRequest.objects.all()
        email = self.request.query_params.get('email', None)
        if email is not None:
            queryset = queryset.filter(email=email)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

# class VendorRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = VendorRequest.objects.all()
#     serializer_class = VendorRequestSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_update(self, serializer):
#         serializer.save()

#     def get_queryset(self):
#         user = self.request.user
#         email = self.request.query_params.get('email', None)
#         if email:
#             return self.queryset.filter(email=email)
#         return self.queryset
    

class VendorRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VendorRequest.objects.all()  # Include both active and inactive requests
    serializer_class = VendorRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        user = User.objects.get(email=serializer.data.get('email'))
        new_status = serializer.data.get('status')

        if new_status == 'approved':
            user.role = 'vendor'
        else:
            user.role = 'customer'
        user.save()

        # Send email notifications based on status changes
        try:
            if new_status == 'approved':
                send_mail(
                    'Vendor Request Approved',
                    f'Dear {user.username},\n\n'
                    'Thank you very much for your interest in joining our platform EasyLife as a vendor. '
                    'We are very pleased to inform you that your request has been approved. You can now log in and upload your products to our platform. '
                    'We look forward to seeing the unique and exciting products you will offer.\n\n'
                    'Here are a few things you can do now:\n'
                    '- Log in to your account and complete your vendor profile.\n'
                    '- Start adding products to your store.\n'
                    '- Explore our vendor dashboard to manage your listings and track your sales.\n\n'
                    'If you have any questions or need assistance, feel free to reach out to our support team.\n\n'
                    'Best regards,\n'
                    'EasyLife Support Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=False,
                )
            elif new_status == 'under_review':
                send_mail(
                    'Vendor Request Under Review',
                    f'Dear {user.username},\n\n'
                    'Thank you very much for your interest in joining our platform EasyLife as a vendor. '
                    'We are writing to inform you that your vendor request is currently under review. '
                    'We will notify you once it is approved.\n\n'
                    'Please be patient as we carefully review your application to ensure all details are in order. '
                    'In the meantime, you can prepare your product listings and get ready to showcase your items on our platform.\n\n'
                    'If you have any questions or need assistance, feel free to reach out to our support team.\n\n'
                    'Best regards,\n'
                    'EasyLife Support Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=False,
                )
            elif new_status == 'rejected':
                send_mail(
                    'Vendor Request Rejected',
                    f'Dear {user.username},\n\n'
                    'Thank you very much for your interest in joining our platform as a vendor. '
                    'We regret to inform you that your vendor request has been rejected. '
                    'Please contact our support team for more information or if you have any questions.\n\n'
                    'We understand this may be disappointing, but we encourage you to review your application details and ensure all information provided is accurate. '
                    'You are welcome to reapply in the future after addressing any issues that may have led to this decision.\n\n'
                    'Best regards,\n'
                    'EasyLife Support Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=False,
                )
        except Exception as e:
            print(f"Error sending email: {e}")

        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status in ['pending', 'under_review']:
            instance.activity = 'inactif'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Only pending or under review requests can be deleted."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
def health_check(request):
    return HttpResponse("Your application is running", content_type="text/plain")