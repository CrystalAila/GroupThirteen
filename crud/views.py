from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, Category# Adjust imports as needed
from decimal import Decimal
from django.contrib import messages
from django.db import models

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def product_list(request):
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.select_related('category').all()
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'products/index.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
    })

def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        category_id = request.POST.get("category")
        purchase_price = request.POST.get("purchase_price")
        selling_price = request.POST.get("selling_price")
        quantity_in_stock = request.POST.get("quantity_in_stock")
        stock_status = request.POST.get("stock_status") == 'True'

        try:
            category = Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist.")
            return redirect('product_list')

        Product.objects.create(
            product_name=product_name,
            category=category,
            purchase_price=purchase_price,
            selling_price=selling_price,
            quantity_in_stock=quantity_in_stock,
            stock_status=stock_status
        )

        messages.success(request, "Product added successfully!") 
        return redirect('product_list')
    
    return redirect('product_list')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/index2.html', {'categories': categories})

def add_category(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if not category_name:
            return render(request, 'categories/index2.html', {'categories': categories, 'error': 'Category name is required.'})
        try:
            category = Category(category_name=category_name)
            category.save()
            categories = Category.objects.all()
            return render(request, 'categories/index2.html', {'categories': categories, 'success': True})
        except Exception as e:
            return render(request, 'categories/index2.html', {'categories': categories, 'error': str(e)})
    return render(request, 'categories/index2.html', {'categories': categories})

def dashboard(request):
    total_products = Product.objects.count()
    total_stock = Product.objects.aggregate(total_stock=models.Sum('quantity_in_stock'))['total_stock'] or 0
    out_of_stock = Product.objects.filter(quantity_in_stock=0).count()
    # total_orders = Order.objects.count() if 'Order' in globals() else 0
    # total_customers = Customer.objects.count() if 'Customer' in globals() else 0
    sold_units = Product.objects.aggregate(sold=models.Sum('sold_units'))['sold'] if 'sold_units' in [f.name for f in Product._meta.fields] else 0

    context = {
        'total_products': total_products,
        'total_stock': total_stock,
        'out_of_stock': out_of_stock,
        # 'total_orders': total_orders,
        # 'total_customers': total_customers,
        'sold_units': sold_units,
    }
    return render(request, 'dashboard/dashboard.html', context)