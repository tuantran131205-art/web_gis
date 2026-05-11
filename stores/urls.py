from django.urls import path
from . import views
from . import dashboard_views

urlpatterns = [
    # Home & Search
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),

    # GIS
    path('find/', views.find_nearest, name='find'),

    # Products
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),

    # Order & Payment
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/result/', views.payment_result, name='payment_result'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Custom Dashboard ─────────────────────────────────────────────────
    path('dashboard/', dashboard_views.dashboard_home, name='dashboard_home'),

    # Stores
    path('dashboard/stores/', dashboard_views.store_list, name='dashboard_store_list'),
    path('dashboard/stores/add/', dashboard_views.store_create, name='dashboard_store_create'),
    path('dashboard/stores/<int:pk>/edit/', dashboard_views.store_edit, name='dashboard_store_edit'),
    path('dashboard/stores/<int:pk>/delete/', dashboard_views.store_delete, name='dashboard_store_delete'),

    # Products
    path('dashboard/products/', dashboard_views.product_list, name='dashboard_product_list'),
    path('dashboard/products/add/', dashboard_views.product_create, name='dashboard_product_create'),
    path('dashboard/products/<int:pk>/edit/', dashboard_views.product_edit, name='dashboard_product_edit'),
    path('dashboard/products/<int:pk>/delete/', dashboard_views.product_delete, name='dashboard_product_delete'),

    # Orders
    path('dashboard/orders/', dashboard_views.order_list, name='dashboard_order_list'),
    path('dashboard/orders/<int:pk>/', dashboard_views.order_detail, name='dashboard_order_detail'),
    path('dashboard/orders/<int:pk>/delete/', dashboard_views.order_delete, name='dashboard_order_delete'),
]

