from django.urls import path, include
from .views import (
    AdminDashboardView, CategoryCreateView, CategoryRetrieveUpdateDestroyView, CategoryViewSet, ClickedProductView, 
    CustomerDashboardView, LogoutView, ProductSearchView, 
    ProductViewAllSet, RegisterView, SearchQueryView, 
    SubscriberCreateView, UserDetailView, UserProfileView, 
    UserViewSet, VendorDashboardView, VendorRequestDetailView, VendorRequestListCreateView, VisitViewSet,
    ProductDetailView, proxy_elasticsearch
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AddressListCreateView, AddressDetailView
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductVariantViewSet, InventoryViewSet, health_check

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'variants', ProductVariantViewSet, basename='variant')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'products-all', ProductViewAllSet, basename='product-all')
router.register(r'users', UserViewSet, basename='user')
router.register(r'visits', VisitViewSet, basename='visit')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('profile/', UserProfileView.as_view(), name='user-profile'), 
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('products/search/', ProductSearchView.as_view(), name='product_search'),
    path('health-check/', health_check, name='health-check'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('vendor/dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path('customer/dashboard/', CustomerDashboardView.as_view(), name='customer-dashboard'),
    path('subscribe/', SubscriberCreateView.as_view(), name='subscribe'),
    path('clicked-products/', ClickedProductView.as_view(), name='clicked-product'),
    path('search-queries/', SearchQueryView.as_view(), name='search-query'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('elasticsearch/<path:path>', proxy_elasticsearch, name='proxy_elasticsearch'),
    path('vendor-requests/', VendorRequestListCreateView.as_view(), name='vendor-requests-list-create'),
    path('vendor-requests/<int:pk>/', VendorRequestDetailView.as_view(), name='vendor-requests-detail'),
    path('category/', CategoryCreateView.as_view(), name='category-create'),
    path('category/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-retrieve-update-destroy'),
    path('', include(router.urls)),
    ]
