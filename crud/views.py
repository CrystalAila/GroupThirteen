from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Product, TransactionItem, Category, Transaction
from decimal import Decimal
from django.contrib import messages
from django.db import models, transaction
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Sum
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.timezone import now
import logging

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if hasattr(request.user, 'role') and request.user.role.role_type in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard')  # <--- THIS CAUSES THE LOOP!
        return _wrapped_view
    return decorator

def manager_required(view_func):
    return role_required(['Manager'])(view_func)

def cashier_or_manager_required(view_func):
    return role_required(['Manager', 'Cashier'])(view_func)


# Create your views here.


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Redirect based on role
            if user.role.role_type == 'Manager':
                return redirect('dashboard')
            elif user.role.role_type == 'Cashier':
                return redirect('cashier_pov')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login/loginpage.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
@manager_required
def product_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    categories = Category.objects.all()
    products = Product.objects.select_related('category').all().order_by('product_name')

    if category_id:
        products = products.filter(category_id=category_id)
    if search_query:
        products = products.filter(product_name__icontains=search_query)

    paginator = Paginator(products, 10)  # 10 products per page
    page_obj = paginator.get_page(page_number)

    # AJAX response for live search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_data = []
        for product in page_obj:
            products_data.append({
                'product_name': product.product_name,
                'category': product.category.category_name,
                'purchase_price': str(product.purchase_price),
                'selling_price': str(product.selling_price),
                'quantity_in_stock': product.quantity_in_stock,
                'product_image': product.product_image.url if product.product_image else '',
                'product_id': product.product_id,
            })
        return JsonResponse({
            'products': products_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })

    # Debug: Print actual stock values to console
    print("=== PRODUCT LIST DEBUG ===")
    for product in products[:5]:  # Show first 5 products for debugging
        print(f"Product: {product.product_name}, Stock: {product.quantity_in_stock}")
    
    # Add stock status indicators - use quantity_in_stock as primary source
    for product in products:
        actual_stock = int(product.quantity_in_stock) if product.quantity_in_stock else 0
        
        if actual_stock == 0:
            product.stock_indicator = 'out-of-stock'
        elif actual_stock <= 5:  # Low stock threshold
            product.stock_indicator = 'low-stock'
        else:
            product.stock_indicator = 'in-stock'
        
        # Add calculated availability for consistency
        product.is_available = actual_stock > 0
        product.actual_stock_count = actual_stock
    
    return render(request, 'products/index.html', {
        'products': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'page_obj': page_obj,
    })

@login_required
@manager_required
def add_product(request):
    if request.method == "POST":
        product_image = request.FILES.get('product_image')
        product_name = request.POST.get("product_name")
        category_id = request.POST.get("category")
        purchase_price = request.POST.get("purchase_price")
        selling_price = request.POST.get("selling_price")
        quantity_in_stock = request.POST.get("quantity_in_stock")

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
            product_image=product_image
        )

        messages.success(request, "Product added successfully!") 
        return redirect('product_list')
    
    return redirect('product_list')

@login_required
@manager_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/index2.html', {'categories': categories})

@login_required
@manager_required
def add_category(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if not category_name:
            messages.error(request, 'Category name is required.')
            return redirect('category_list')
        try:
            category = Category(category_name=category_name)
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('category_list')
    return render(request, 'categories/index2.html', {'categories': categories})

@login_required
@manager_required
def dashboard(request):
    total_products = Product.objects.count()
    total_stock = Product.objects.aggregate(total=Sum('quantity_in_stock'))['total'] or 0
    out_of_stock = Product.objects.filter(quantity_in_stock=0).count()
    sold_units = TransactionItem.objects.aggregate(total=Sum('quantity'))['total'] or 0

    # Pie chart data: units sold per category
    category_sales = (
        TransactionItem.objects
        .values('product__category__category_name')
        .annotate(units_sold=Sum('quantity'))
    )
    pie_labels = [c['product__category__category_name'] for c in category_sales]
    pie_data = [c['units_sold'] for c in category_sales]

    return render(request, 'dashboard/dashboard.html', {
        'total_products': total_products,
        'total_stock': total_stock,
        'sold_units': sold_units,
        'out_of_stock': out_of_stock,
        'pie_labels': pie_labels,
        'pie_data': pie_data,
    })

@login_required
@manager_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    categories = Category.objects.all() 
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.category_id = request.POST.get('category')
        product.purchase_price = request.POST.get('purchase_price')
        product.selling_price = request.POST.get('selling_price')
        product.quantity_in_stock = request.POST.get('quantity_in_stock')

        if request.FILES.get('product_image'):
            product.product_image = request.FILES['product_image']
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('product_list')
    return render(request, 'products/index.html', {
        'product': product,
        'categories': categories
    })

@login_required
@manager_required
def edit_category(request, category_id):
    from django.shortcuts import get_object_or_404
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.category_name = request.POST.get('category_name')
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('category_list')
    return render(request, 'categories/EditCategory.html', {
        'category': category
    })

@login_required
@manager_required
def delete_product(request, product_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
    return redirect('product_list')

@login_required
@manager_required
def delete_category(request, category_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    return redirect('category_list')

@login_required
@cashier_or_manager_required
def cashier_pov(request):
    products = Product.objects.select_related('category').all().order_by('product_name')
    categories = Category.objects.all()

    # Debug: Print actual stock values to console
    print("=== CASHIER POV DEBUG ===")
    for product in products[:5]:  # Show first 5 products for debugging
        print(f"Product: {product.product_name}, Stock: {product.quantity_in_stock}")

    # Add stock status and availability info for each product
    for product in products:
        actual_stock = int(product.quantity_in_stock) if product.quantity_in_stock else 0
        product.is_available = actual_stock > 0

        if actual_stock == 0:
            product.stock_status_text = 'Out of Stock'
            product.stock_class = 'out-of-stock'
        elif actual_stock <= 5:
            product.stock_status_text = f'Low Stock ({actual_stock} left)'
            product.stock_class = 'low-stock'
        else:
            product.stock_status_text = f'{actual_stock} in stock'
            product.stock_class = 'in-stock'

        product.calculated_stock_status = actual_stock > 0

    return render(request, 'cashier/cashier_pov.html', {
        'products': products,
        'categories': categories,
    })


@csrf_exempt
def get_product_stock(request):
 
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        try:
            product = Product.objects.get(pk=product_id)
            return JsonResponse({
                'status': 'success',
                'stock': product.quantity_in_stock,
                'available': product.quantity_in_stock > 0,
                'product_name': product.product_name
            })
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def check_stock_availability(request):
  
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_items = data.get('cart', [])
        availability_results = []
        
        for item in cart_items:
            try:
                product = Product.objects.get(pk=item['pk'])
                requested_qty = int(item['qty'])
                is_available = product.quantity_in_stock >= requested_qty
                
                availability_results.append({
                    'product_id': item['pk'],
                    'product_name': product.product_name,
                    'requested_qty': requested_qty,
                    'available_stock': product.quantity_in_stock,
                    'is_available': is_available,
                    'message': f"Only {product.quantity_in_stock} available" if not is_available else "Available"
                })
            except Product.DoesNotExist:
                availability_results.append({
                    'product_id': item['pk'],
                    'is_available': False,
                    'message': 'Product not found'
                })
        
        all_available = all(item['is_available'] for item in availability_results)
        
        return JsonResponse({
            'status': 'success',
            'all_available': all_available,
            'items': availability_results
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def update_stock(request):
   
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_items = data.get('cart', [])
        updated_products = []
        errors = []
        
        # First, check if all items have sufficient stock
        for item in cart_items:
            try:
                product = Product.objects.get(pk=item['pk'])
                requested_qty = int(item['qty'])
                if product.quantity_in_stock < requested_qty:
                    errors.append(f"{product.product_name}: Only {product.quantity_in_stock} available, {requested_qty} requested")
            except Product.DoesNotExist:
                errors.append(f"Product with ID {item['pk']} not found")
        
        # If there are stock issues, return error
        if errors:
            return JsonResponse({
                'status': 'error',
                'message': 'Insufficient stock',
                'errors': errors
            }, status=400)
        
        # If all checks pass, update the stock
        for item in cart_items:
            try:
                product = Product.objects.get(pk=item['pk'])
                old_stock = product.quantity_in_stock
                product.quantity_in_stock = max(product.quantity_in_stock - int(item['qty']), 0)
                product.save()
                
                updated_products.append({
                    'product_id': product.pk,
                    'product_name': product.product_name,
                    'old_stock': old_stock,
                    'new_stock': product.quantity_in_stock,
                    'qty_sold': int(item['qty'])
                })
            except Product.DoesNotExist:
                continue
        
        return JsonResponse({
            'status': 'success',
            'message': 'Stock updated successfully',
            'updated_products': updated_products
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def refresh_products(request):
   
    if request.method == 'GET':
        category_id = request.GET.get('category')
        products = Product.objects.select_related('category').all()
        
        if category_id:
            products = products.filter(category_id=category_id)
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.pk,
                'name': product.product_name,
                'category': product.category.category_name,
                'price': str(product.selling_price),
                'stock': product.quantity_in_stock,
                'available': product.quantity_in_stock > 0,
                'stock_status': 'out-of-stock' if product.quantity_in_stock == 0 else 'low-stock' if product.quantity_in_stock <= 5 else 'in-stock',
                'image_url': product.product_image.url if product.product_image else None
            })
        
        return JsonResponse({
            'status': 'success',
            'products': products_data
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@cashier_or_manager_required
@csrf_exempt  # Only for testing; remove in production and use CSRF token!
def process_purchase(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            amount_paid = data.get('amount_paid')
            if not cart:
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)
            if amount_paid is None:
                return JsonResponse({'status': 'error', 'message': 'Amount paid is missing'}, status=400)
            amount_paid = Decimal(str(amount_paid))
            cashier_name = request.user.get_full_name() if hasattr(request.user, 'get_full_name') else request.user.username

            total_amount = Decimal('0')
            for item in cart:
                if 'pk' not in item or 'qty' not in item:
                    return JsonResponse({'status': 'error', 'message': 'Cart item missing pk or qty'}, status=400)
                product = Product.objects.get(pk=item['pk'])
                qty = int(item['qty'])
                total_amount += product.selling_price * qty

            # Create Transaction
            transaction = Transaction.objects.create(
                cashier_name=cashier_name,
                total_amount=total_amount,
                amount_paid=amount_paid,
            )

            # Create TransactionItems and update stock
            for item in cart:
                product = Product.objects.get(pk=item['pk'])
                qty = int(item['qty'])
                # Deduct stock
                product.quantity_in_stock = max(product.quantity_in_stock - qty, 0)
                product.units_sold += qty
                product.save()
                # Record transaction item
                TransactionItem.objects.create(
                    transaction=transaction,
                    product=product,
                    quantity=qty,
                    price_at_purchase=product.selling_price,
                )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            import logging
            logging.exception("Error in process_purchase")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@cashier_or_manager_required
@csrf_exempt
def complete_purchase(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)

    try:
        data = json.loads(request.body)
        cart_items = data.get('cartItems', [])
        cashier_name = data.get('cashier_name', 'Unknown Cashier')
        amount_paid = Decimal(str(data.get('amount_paid', '0')))  # Get amount_paid or 0 if missing

        if not cart_items:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

        product_ids = [int(item['product_id']) for item in cart_items]  # Ensure IDs are integers
        products = Product.objects.filter(product_id__in=product_ids)

        # Create a map of product_id -> product
        products_map = {p.product_id: p for p in products}

        total_amount = Decimal('0')

        # Validate all products exist and have enough stock
        for item in cart_items:
            pid = int(item['product_id'])  # Ensure product_id is an integer
            qty = int(item.get('quantity', 0))

            # Check if product exists in the products_map (which contains products fetched from DB)
            if pid not in products_map:
                raise Exception(f'Product ID {pid} not found.')

            product = products_map[pid]

            # Check if there's enough stock for the product
            if product.quantity_in_stock < qty:
                raise Exception(f'Not enough stock for product {product.product_name}.')

            # Accumulate the total amount for the purchase
            total_amount += product.selling_price * qty

        # Check if amount paid is sufficient
        if amount_paid < total_amount:
            raise Exception(f'Amount paid ({amount_paid}) is less than total amount ({total_amount}).')

        # Create Transaction
        transaction_record = Transaction.objects.create(
            cashier_name=cashier_name,
            total_amount=total_amount,
            amount_paid=amount_paid,
        )

        # Create TransactionItems and update Products
        for item in cart_items:
            pid = int(item['product_id'])  # Ensure product_id is an integer
            qty = int(item.get('quantity', 0))
            product = products_map[pid]

            # Create TransactionItem
            TransactionItem.objects.create(
                transaction=transaction_record,
                product=product,
                quantity=qty,
                price_at_purchase=product.selling_price
            )

            # Update product stock and units sold
            product.quantity_in_stock -= qty
            product.units_sold += qty
            product.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Purchase completed successfully!',
            'transaction_id': transaction_record.transaction_id,
            'total_amount': str(total_amount)
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error completing purchase: {str(e)}'}, status=400)

@login_required
@cashier_or_manager_required
def receipt_view(request, transaction_id):
    # Example item data, replace with your actual query logic
    items = [
        {"name": "Apple", "quantity": 3, "price": 25.0},
        {"name": "Banana", "quantity": 2, "price": 15.5},
    ]

    # Calculate total price per item
    for item in items:
        item['total_price'] = item['price'] * item['quantity']

    total = sum(item['total_price'] for item in items)
    cash = 100.0
    change = cash - total

    context = {
        "transaction_id": transaction_id,
        "cashier": "Alice",
        "items": items,
        "total": total,
        "cash": cash,
        "change": change,
        "now": now(),
    }
    return render(request, "cashier/receipt.html", context)
