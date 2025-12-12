# delivery_calculator/urls.py (your main project urls.py)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculator.urls')),  # Calculator at root
]