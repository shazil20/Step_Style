from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from djoser import views as djoser_views


# Define your viewsets
router = DefaultRouter()
router.register(r'products', ProductViewSet)
# router.register(r'cart', CartViewSet, basename='cart')
# router.register(r'users', djoser_views.UserViewSet)





# Add your custom URL patterns
urlpatterns = [
    # URL patterns generated by router
    *router.urls,
    # path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),

    path('product-list/', ProductList.as_view(), name='products-list'),
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('logout/', UserLogoutAPIView.as_view(), name='user_logout'),
    path('users/', CustomUserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', CustomUserRetrieveUpdateDestroyAPIView.as_view(),
         name='user-detail'),
    path('users/<int:user_id>/orders/status/', update_order_status, name='update_order_status'),
    path('user-cart/', UserCartView.as_view(), name='user_cart'),
    path('add-to-cart/<int:user_id>/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),
    # path('auth/token/login/', CustomLoginView.as_view(), name='login'),
]