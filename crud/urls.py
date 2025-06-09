from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/list/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('categories/list/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('', views.index, name='index'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
