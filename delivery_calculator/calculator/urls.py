# calculator/urls.py (your app's urls.py)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculator_view, name='calculator'),
    path('calculate/', views.calculate_price_api, name='calculate_price'),
]