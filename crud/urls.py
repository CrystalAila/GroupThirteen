from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect base URL to login page
    path('', RedirectView.as_view(url='/login/', permanent=False)),

    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('products/list/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),

    path('categories/list/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),

    path('cashier/', views.cashier_pov, name='cashier_pov'),

    path('update-stock/', views.update_stock, name='update_stock'),
    path('api/product-stock/', views.get_product_stock, name='get_product_stock'),
    path('api/check-stock/', views.check_stock_availability, name='check_stock_availability'),
    path('api/refresh-products/', views.refresh_products, name='refresh_products'),
    path('process_purchase/', views.process_purchase, name='process_purchase'),
    path('complete_purchase/', views.complete_purchase, name='complete_purchase'),
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
