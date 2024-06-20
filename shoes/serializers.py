from .models import *
from rest_framework import serializers, response


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'color', 'size', 'price', 'product_picture']

class CartSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'products']

class OrderSerializer(serializers.Serializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'products']

