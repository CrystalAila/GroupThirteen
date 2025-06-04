from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/list/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('categories/list/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('', views.index, name='index'),
]
