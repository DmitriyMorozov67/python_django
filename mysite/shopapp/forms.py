from django.forms import ModelForm
from django.contrib.auth.models import Group
from django.core.validators import validate_image_file_extension
from django import forms

from .models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True})
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = 'delivery_address', 'promocode', 'user', 'products'

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
