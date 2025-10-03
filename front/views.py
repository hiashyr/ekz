def contacts_view(request):
    return render(request, 'pages/contacts.html')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import (
    CustomUserCreationForm, 
    PhoneAuthForm,
    EmailAuthForm,
    UsernameAuthForm,
    CartItemQuantityForm,
    OrderForm
)
from .models import (
    Category,
    Product,
    CartItem,
    Order,
    OrderItem
)

def main_page(request):
    # Get popular products for display
    popular_products = Product.objects.all()[:8]
    context = {
        'popular_products': popular_products
    }
    return render(request, 'pages/main_page.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Используем ModelBackend в качестве бэкенда аутентификации по умолчанию
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main_page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'components/register.html', {'form': form})

def login_view(request):
    auth_type = request.POST.get('auth_type', request.GET.get('tab', 'username'))
    
    if request.method == 'POST':
        if auth_type == 'phone':
            form = PhoneAuthForm(request.POST)
        elif auth_type == 'email':
            form = EmailAuthForm(request.POST)
        else:
            form = UsernameAuthForm(request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main_page')
    else:
        if auth_type == 'phone':
            form = PhoneAuthForm()
        elif auth_type == 'email':
            form = EmailAuthForm()
        else:
            form = UsernameAuthForm()
    
    return render(request, 'components/login.html', {
        'form': form,
        'active_tab': auth_type
    })

def logout_view(request):
    logout(request)
    return redirect('main_page')

# 1. Каталог с фильтрацией
def catalog_view(request):
    categories = Category.objects.all()
    
    # Получение фильтров из GET-параметров
    category_id = request.GET.get('category')
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Начинаем с полной выборки товаров
    products = Product.objects.all()
    
    # Применяем фильтры
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    context = {
        'categories': categories,
        'products': products,
        'selected_category': category_id,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price
    }
    
    return render(request, 'pages/catalog.html', context)

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product}
    return render(request, 'pages/product_detail.html', context)

# 2. Корзина
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Подсчет общей суммы корзины
    total_amount = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    
    return render(request, 'pages/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Проверяем, нет ли уже такого товара в корзине
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    # Если товар уже был в корзине, увеличиваем количество
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = CartItemQuantityForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

# 4. Формирование заказа
@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Если корзина пуста, перенаправляем в корзину
    if not cart_items.exists():
        return redirect('cart')
    
    # Подсчет общей суммы заказа
    total_amount = sum(item.get_total() for item in cart_items)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total_amount
            order.save()
            
            # Добавляем товары из корзины в заказ
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Очищаем корзину пользователя
            cart_items.delete()
            
            return redirect('order_success', order_id=order.id)
    else:
        # Предзаполняем форму данными из профиля пользователя
        initial_data = {
            'shipping_address': request.user.address,
            'phone': request.user.phone,
            'email': request.user.email
        }
        form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    
    return render(request, 'pages/checkout.html', context)

@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    
    return render(request, 'pages/order_success.html', context)

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'pages/orders.html', context)

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'pages/order_detail.html', context)

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        # Handle form submission for profile update
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.city = request.POST.get('city', user.city)
        user.country = request.POST.get('country', user.country)
        
        # Handle avatar update
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        user.save()
        return redirect('profile')
    
    # Get user's orders
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'orders': orders
    }
    
    return render(request, 'pages/profile.html', context)