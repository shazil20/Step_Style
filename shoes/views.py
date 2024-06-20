import status
from django.db import IntegrityError
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from django.contrib.auth import authenticate, login
from .models import *
from django.contrib.auth import logout
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response




class CustomUserListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CustomUserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



@api_view(['PUT'])
@permission_classes([AllowAny])
def update_order_status(request, user_id):
    try:
        orders = Order.objects.filter(user_id=user_id)
        if not orders.exists():
            return Response({'message': 'Orders not found'}, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    status_update = request.data.get('status')
    if status_update in dict(Order.STATUS_CHOICES):
        orders.update(status=status_update)
        return Response({'message': 'Order status updated successfully'})
    else:
        return Response({'message': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)


class CheckoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        # Create orders from cart items
        for cart_item in cart_items:
            Order.objects.create(
                user=cart_item.user,
                product=cart_item.product,
                price=cart_item.price,
                quantity=cart_item.quantity,
                status=cart_item.status
            )

        # Delete cart items
        cart_items.delete()

        return Response({'message': 'Orders placed successfully'}, status=status.HTTP_201_CREATED)

class UserCartView(APIView):
    permission_classes = [AllowAny]


    def get(self, request):
        # Retrieve the logged-in user
        user = request.user

        # Retrieve the cart items associated with the logged-in user
        cart_items = Cart.objects.filter(user=user)

        # Serialize the cart items data
        cart_data = []
        for item in cart_items:
            image_url = request.build_absolute_uri(
                item.product.product_picture.url) if item.product.product_picture else None
            cart_data.append({
                'product_id' : item.product.id,
                'product_name': item.product.name,
                'price': item.price,
                'quantity': item.quantity,
                'image_url': image_url
            })

        return JsonResponse({'cart_items': cart_data})

# class AddToCartView(APIView):
#     permission_classes = [AllowAny]
#
#
#     def post(self, request, user_id, product_id):
#         user = get_object_or_404(CustomUser, id=user_id)
#         product = get_object_or_404(Product, id=product_id)
#         price = request.data.get('price')
#         quantity = request.data.get('quantity')
#
#
#         # Create the Cart object
#         cart_item = Cart.objects.create(user=user, product=product, price=price, quantity=quantity)
#
#         return JsonResponse({'message': 'Product added to cart successfully'})

class AddToCartView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id, product_id):
        user = get_object_or_404(CustomUser, id=user_id)
        product = get_object_or_404(Product, id=product_id)
        price = request.data.get('price')
        quantity = request.data.get('quantity')

        # Check if the product is already in the cart
        try:
            cart_item = Cart.objects.get(user=user, product=product)
            # Update the existing cart item
            cart_item.price += int(price)
            cart_item.quantity += int(quantity)  # Increment the quantity
            cart_item.save()
            return JsonResponse({'message': 'Product updated in cart successfully'})
        except Cart.DoesNotExist:
            # Create the Cart object if it doesn't exist
            Cart.objects.create(user=user, product=product, price=price, quantity=quantity)
            return JsonResponse({'message': 'Product added to cart successfully'})

    def delete(self, request, user_id, product_id):
        user = get_object_or_404(CustomUser, id=user_id)
        product = get_object_or_404(Product, id=product_id)

        # Delete the Cart object if it exists
        cart_item = get_object_or_404(Cart, user=user, product=product)
        cart_item.delete()

        return JsonResponse({'message': 'Product removed from cart successfully'})

class ProductList(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)





class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:

            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)

            # Get profile photo URL (assuming a `profile_photo` field exists)
            profile_photo_url = None
            if user.profile_photo:
                profile_photo_url = request.build_absolute_uri(user.profile_photo.url)

            return Response({
                'access': str(refresh.access_token),
                'refresh': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'email': user.email,
                    'profile_photo_url': profile_photo_url
                }
            })
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)





class UserLogoutAPIView(APIView):
    def post(self, request):
        if request.method == 'POST':
            logout(request)
            return JsonResponse({'message': 'User logged out successfully.'})
        else:
            return JsonResponse({'error': 'Method not allowed.'}, status=405)


class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        profile_photo = data.get('profile_photo')
        email = data.get('email')
        role = data.get('role', 'user')

        if not username or not password or not email:
            return JsonResponse({'error': 'Username, password, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.create_user(username=username, password=password,
                                                  profile_photo=profile_photo, email=email)
            user.role = role
            user.save()

            return JsonResponse({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            if 'UNIQUE constraint failed: custom_user.username' in str(e):
                return JsonResponse({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'error': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
