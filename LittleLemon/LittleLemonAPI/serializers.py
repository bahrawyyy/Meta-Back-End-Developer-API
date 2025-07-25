from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']
        read_only_fields = ['id']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), write_only=True
    )


    def validate(self, data):
        if data['price'] <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return data

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        read_only_fields = ['id']  # id is automatically generated, so it should be read-only




class CartSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        source='menuitem', queryset=MenuItem.objects.all(), write_only=True
    )
    item = MenuItemSerializer(source='menuitem', read_only=True)

    class Meta:
        model = Cart
        fields = ['menu_item', 'item', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']

    def validate(self, data):
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return data

    def create(self, validated_data):
        menu_item = validated_data['menuitem']
        quantity = validated_data['quantity']
        validated_data['unit_price'] = menu_item.price
        validated_data['price'] = quantity * menu_item.price
        return super().create(validated_data)

