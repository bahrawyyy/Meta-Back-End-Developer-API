from django.urls import path 
from . import views


urlpatterns = [
    path('users/', views.users),
    path('users/users/me', views.display_current_user),
    path('menu-items/', views.menu_items),
    path('menu-items/<int:menuItem>/', views.menu_item_detail, name='menu_item_detail'),
    path('groups/<str:group_name>/users', views.group_user, name='group_user'),
    path('groups/<str:group_name>/users/<int:user_id>/', views.remove_user_from_group, name='remove_user_from_group'),
    path('cart/menu-items/', views.manage_cart, name='manage_cart'),
    path('orders/', views.manage_order, name='manage_order'),
    path('orders/<int:order_id>/', views.manager_specific_order, name='manager_specific_order'),
]