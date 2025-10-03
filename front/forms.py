from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from .models import (
    CustomUser, Product, Category, CartItem, Order
)
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
        help_text='Введите номер телефона в формате +7XXXXXXXXXX'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 
                 'password1', 'password2', 'avatar')
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Проверка формата номера телефона для России
            if not re.match(r'^\+7\d{10}$', phone):
                raise ValidationError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return phone

class PhoneAuthForm(forms.Form):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
        help_text='Введите номер телефона в формате +7XXXXXXXXXX'
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Проверка формата номера телефона для России
            if not re.match(r'^\+7\d{10}$', phone):
                raise ValidationError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        password = cleaned_data.get('password')

        if phone and password:
            self.user = authenticate(phone=phone, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный телефон или пароль")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

class EmailAuthForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

class UsernameAuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный логин или пароль")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category']

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartItemQuantityForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

class OrderForm(forms.ModelForm):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
        help_text='Введите номер телефона в формате +7XXXXXXXXXX'
    )
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone', 'email']
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not re.match(r'^\+7\d{10}$', phone):
                raise ValidationError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return phone