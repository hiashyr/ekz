from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    # Переопределение стандартных полей
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        null=True,
        blank=True
    )
    
    # Дополнительные поля
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True
    )
    
    address = models.TextField(
        _('address'),
        blank=True
    )
    
    age = models.IntegerField(
        _('age'),
        null=True,
        blank=True
    )
    
    birth_date = models.DateField(
        _('birth date'),
        null=True,
        blank=True
    )
    
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
    ]
    gender = models.CharField(
        _('gender'),
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True
    )
    
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True
    )
    
    occupation = models.CharField(
        _('occupation'),
        max_length=100,
        blank=True
    )
    
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        full_name = self.get_full_name()
        if full_name.strip():
            return full_name
        return self.username

# 1. Модели для каталога
class Category(models.Model):
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='categories/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def __str__(self):
        return self.name or ''

class Product(models.Model):
    name = models.CharField(_('name'), max_length=200, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
    
    def __str__(self):
        return self.name or ''

# 2. Модель для корзины
class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('quantity'), default=1, blank=True, null=True)
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else ''}"
    
    def get_total(self):
        if self.product and self.product.price and self.quantity:
            return self.product.price * self.quantity
        return 0

# 3. Модели для заказов
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='orders', blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    shipping_address = models.TextField(_('shipping address'), blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('email'), blank=True, null=True)
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username if self.user else ''}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('quantity'), default=1, blank=True, null=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else ''}"
    
    def get_total(self):
        if self.price and self.quantity:
            return self.price * self.quantity
        return