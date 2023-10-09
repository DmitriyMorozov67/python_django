from django.urls import path
from .views import ClassBasedView
app_name = "blogapp"

urlpatterns = [
    path('article/', ClassBasedView.as_view(), name='blog'),
]