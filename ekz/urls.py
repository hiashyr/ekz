from django.contrib import admin
from django.urls import path
from front import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Администрирование и аутентификация
    path('admin/', admin.site.urls, name='admin'),
    path('', views.main_page, name='main_page'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # 1. Каталог товаров
    path('catalog/', views.catalog_view, name='catalog'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    
    # 2. Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # 4. Заказы
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('orders/', views.orders_view, name='orders'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)