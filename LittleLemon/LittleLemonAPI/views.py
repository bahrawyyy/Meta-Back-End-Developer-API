from django.shortcuts import render
from .models import User, MenuItem, Group, Cart, OrderItem, Order
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import status
from .serializers import MenuItemSerializer, CartSerializer
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

@api_view(['POST'])
def users(request):
    # Create a new user with the username, password, and email from body
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'Username, password, and email are required'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({'message': 'User created successfully', 'user_id': user.id}, status=201)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_current_user(request):
    user = request.user
    return Response({'username': user.username, 'email': user.email})


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == 'GET' and request.user.groups.filter(name__in=['customer', 'delivery-crew', 'manager']).exists():
        queryset = MenuItem.objects.all().order_by('id')

        title = request.query_params.get('title')
        price_lte = request.query_params.get('price')
        category = request.query_params.get('category')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if price_lte:
            queryset = queryset.filter(price__lte=price_lte)
        if category:
            queryset = queryset.filter(category__title=category)


        # Apply Pagination
        page_number = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 3)
        paginator = PageNumberPagination()
        paginator.page = page_number  # Set the current page
        paginator.page_size = per_page  # Set the page size
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        serializer = MenuItemSerializer(paginated_queryset, many=True)
        return Response({'menu_items': serializer.data}, status=status.HTTP_200_OK)

    if request.method == 'POST' and request.user.groups.filter(name='manager').exists():
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Menu item created successfully', 'menu_item': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # For all other methods
    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)



@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item_detail(request, menuItem):
    if request.method == 'GET' and request.user.groups.filter(name__in=['customer', 'delivery-crew', 'manager']).exists():
        menu_items = MenuItem.objects.filter(id=menuItem)
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response({'menu_items': serializer.data}, status=status.HTTP_200_OK)
    
    if request.method in ['PUT', 'PATCH', 'DELETE'] and request.user.groups.filter(name='manager').exists():
        menu_item = MenuItem.objects.filter(id=menuItem).first()
        if not menu_item:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PUT':
            serializer = MenuItemSerializer(menu_item, data=request.data)
        elif request.method == 'PATCH':
            serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
        elif request.method == 'DELETE':
            menu_item.delete()
            return Response({'message': 'Menu item deleted successfully'}, status=status.HTTP_200_OK)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Menu item updated successfully', 'menu_item': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_user(request, group_name):
    if group_name not in ['manager', 'delivery-crew'] or not Group.objects.filter(name=group_name).exists():
        return Response({'error': 'Invalid group name'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET' and request.user.groups.filter(name='manager').exists():
        # display all users in the specified group
        users = User.objects.filter(groups__name=group_name)
        user_data = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
        return Response({'users': user_data}, status=status.HTTP_200_OK)

    if request.method == 'POST' and request.user.groups.filter(name='manager').exists():
        # Assign the user in the payload to the Manager group
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.groups.add(Group.objects.get(name=group_name))
        return Response({'message': f'User {user.username} added to {group_name} group'}, status=status.HTTP_200_OK)

    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_user_from_group(request, group_name, user_id):
    if not request.user.groups.filter(name='manager').exists():
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    group = Group.objects.filter(name=group_name).first()
    if not group or group_name not in ['manager', 'delivery-crew']:
        return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    user.groups.remove(group)
    return Response({'message': f'User {user.username} removed from {group_name} group'}, status=status.HTTP_200_OK)


@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_cart(request):
    if not request.user.groups.filter(name='customer').exists():
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        # check if item is in the cart, if so add its quantity to the existing item
        menu_item = request.data.get('menu_item')
        cart_item = Cart.objects.filter(user=request.user, menuitem=menu_item).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
            return Response({'message': 'Item quantity updated', 'cart_item': CartSerializer(cart_item).data}, status=status.HTTP_200_OK)

        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'Item added to cart', 'cart_item': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response({'cart_items': serializer.data}, status=status.HTTP_200_OK)
    

    if request.method == 'DELETE': # Delete all records in the Cart registerd by that user
        Cart.objects.filter(user=request.user).delete()
        return Response({f'Cart Items deleted Successfully for {request.user}'}, status=status.HTTP_200_OK) 
    

    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_order(request):
    if not request.user.groups.filter(name__in=['customer', 'manager', 'delivery-crew']).exists():
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET' and request.user.groups.filter(name='manager').exists():
        # Returns all orders with order items created by all users
        # Apply filtering and searching

        date = request.data.get('date')
        status_got = request.data.get('status')
        total_lte = request.data.get('total')
        user = request.data.get('user')
        delivery_crew = request.data.get('delivery_crew')

        orders = Order.objects.all()

        if date:
            orders = orders.filter(date=date)
        if status_got:
            orders = orders.filter(status=status_got)
        if total_lte:
            orders = orders.filter(total__lte=total_lte)
        if user:
            orders = orders.filter(user__id=user)  # or user__username if using usernames
        if delivery_crew:
            orders = orders.filter(delivery_crew__id=delivery_crew)  # or delivery_crew__username

        order_data = []
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            item_data = []
            for item in order_items:
                item_data.append({
                    'menuitem': item.menuitem.title,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'price': item.price
                })
            order_data.append({
                'order_id': order.id,
                'user': order.user.username,
                'total': order.total,
                'date': order.date,
                'items': item_data
            })
        return Response({'orders': order_data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and request.user.groups.filter(name='delivery-crew').exists():
        # Returns all orders with order items assigned to the delivery crew
        orders = Order.objects.filter(delivery_crew=request.user)
        order_data = []
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            item_data = []
            for item in order_items:
                item_data.append({
                    'menuitem': item.menuitem.title,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'price': item.price
                })
            order_data.append({
                'order_id': order.id,
                'user': order.user.username,
                'total': order.total,
                'date': order.date,
                'items': item_data
            })
        return Response({'orders': order_data}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        # Logic to create an order
        """
        Creates a new order item for the current user. Gets current cart items from the cart endpoints and adds those items to the order items table. Then deletes all items from the cart for this user.
        """
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            total=0,  # Assuming total is the sum of all items in the cart
            date=timezone.now()  # Assuming date is the current date
        )

        total_price = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            total_price = total_price + item.price

        order.total = total_price
        order.save()

        cart_items.delete()
        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        # Returns all orders with order items created by this user
        orders = Order.objects.filter(user=request.user)
        order_data = []
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            item_data = []
            for item in order_items:
                item_data.append({
                    'menuitem': item.menuitem.title,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'price': item.price
                })
            order_data.append({
                'order_id': order.id,
                'total': order.total,
                'date': order.date,
                'items': item_data
            })
        return Response({'orders': order_data}, status=status.HTTP_200_OK)

    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)



@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manager_specific_order(request, order_id):
    if request.method == 'GET' and request.user.groups.filter(name='delivery-crew').exists():
        if not Order.objects.filter(id=order_id, delivery_crew=request.user).exists():
            return Response({'error': 'Order not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)
        
        order = Order.objects.get(id=order_id, delivery_crew=request.user)
        order_items = OrderItem.objects.filter(order=order)
        item_data = []

        for item in order_items:
            item_data.append({
                'menuitem': item.menuitem.title,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'price': item.price
            })

        return Response({'order_id': order.id, 'items': item_data}, status=status.HTTP_200_OK)
    

    if request.method == 'PATCH' and request.user.groups.filter(name='delivery-crew').exists():
        status_data = request.data.get('status')
        if not status_data:
            return Response({'error': 'Unauthorized Update'})

        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        order.status = status_data
        order.save()
        return Response({'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)

    if request.method in ['PUT', 'PATCH', 'DELETE'] and request.user.groups.filter(name='manager').exists():
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.method in ['PUT', 'PATCH']:
            # Assign delivery Crew
            delivery_crew = request.data.get('delivery_crew')
            if not delivery_crew:
                return Response({'error': 'Delivery crew is required'}, status=status.HTTP_400_BAD_REQUEST)
            crew_member = User.objects.filter(id=delivery_crew).first()
            if not crew_member or not crew_member.groups.filter(name='delivery-crew').exists():
                return Response({'error': 'Invalid delivery crew'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.delivery_crew = crew_member
            order.save()
            return Response({'message': 'Delivery crew assigned successfully'}, status=status.HTTP_200_OK)
        
        if request.method == 'DELETE':
            order.delete()
            return Response({'message': 'Order deleted successfully'}, status=status.HTTP_200_OK)
        

    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)