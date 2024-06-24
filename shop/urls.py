from django.urls import path, include
from .views import LogoutView, ProductViewAllSet, RegisterView, UserDetailView, UserProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AddressListCreateView, AddressDetailView
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, ProductVariantViewSet, InventoryViewSet, health_check

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'variants', ProductVariantViewSet, basename='variant')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'products-all', ProductViewAllSet, basename='product-all')

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
    path('health-check/', health_check, name='health-check'),
    path('', include(router.urls)),
    ]
