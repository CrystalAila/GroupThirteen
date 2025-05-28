from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Products, Categories
from decimal import Decimal

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def product_list(request):
    products = Products.objects.select_related('category_name').all()  # FIXED: use the correct ForeignKey field name
    return render(request, 'products/index.html', {'products': products})

def add_product(request):
    categories = Categories.objects.all()
    if request.method == 'POST':
        product_name = request.POST.get('product_name', '').strip()
        category_id = request.POST.get('category')
        quantity_in_stock = request.POST.get('quantity_in_stock')
        purchase_price = request.POST.get('purchase_price')
        selling_price = request.POST.get('selling_price')
        stock_status = request.POST.get('stock_status') == 'True'

        # Validate required fields
        if not (product_name and category_id and quantity_in_stock and purchase_price and selling_price):
            return render(request, 'products/Add_Product.html', {
                'categories': categories,
                'error': 'All fields are required.'
            })

        try:
            product = Products(
                product_name=product_name,
                category_name_id=category_id,  # <-- FIXED: match your model field name
                quantity_in_stock=int(quantity_in_stock),
                purchase_price=Decimal(purchase_price),
                selling_price=Decimal(selling_price),
                stock_status=stock_status,
            )
            product.save()
            return redirect('product_list')
        except Exception as e:
            return render(request, 'products/Add_Product.html', {
                'categories': categories,
                'error': f"Error: {str(e)}"
            })
    return render(request, 'products/Add_Product.html', {'categories': categories})

def category_list(request):
    categories = Categories.objects.all()
    return render(request, 'categories/index2.html', {'categories': categories})

def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if not category_name:
            return render(request, 'categories/AddCategory.html', {'error': 'Category name is required.'})
        try:
            category = Categories(category_name=category_name)
            category.save()
            return render(request, 'categories/AddCategory.html', {'success': True})
        except Exception as e:
            return render(request, 'categories/AddCategory.html', {'error': str(e)})
    return render(request, 'categories/AddCategory.html')