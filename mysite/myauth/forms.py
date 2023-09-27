from django import forms
from django.forms import ModelForm
from .models import Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "username", "name", "last_name", "email", "bio"
