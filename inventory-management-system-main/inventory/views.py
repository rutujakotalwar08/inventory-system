from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category, Supplier, Product, StockTransaction
from .forms import CategoryForm, SupplierForm, ProductForm, StockTransactionForm
from .serializers import ProductSerializer, StockTransactionSerializer

# --- Web Views ---

@login_required
def dashboard(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_stock_value = Product.objects.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
    low_stock_products = Product.objects.filter(quantity__lte=F('minimum_stock'))
    recent_transactions = StockTransaction.objects.order_by('-date')[:5]

    # Simple logic for chart (last 7 days transactions)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_txs = StockTransaction.objects.filter(date__gte=seven_days_ago)
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_stock_value': total_stock_value,
        'low_stock_products': low_stock_products,
        'recent_transactions': recent_transactions,
        'chart_data': {
            'labels': [tx.date.strftime('%b %d') for tx in recent_txs],
            'in_data': [tx.quantity if tx.transaction_type == 'IN' else 0 for tx in recent_txs],
            'out_data': [tx.quantity if tx.transaction_type == 'OUT' else 0 for tx in recent_txs],
        }
    }
    return render(request, 'inventory/dashboard.html', context)

# CRUD for Products
@login_required
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)
        
    categories = Category.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products, 'categories': categories})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

# CRUD for Categories (simplified list/create in one for demo, or separated)
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Add Category', 'back_url': 'category_list'})

# Suppliers
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Add Supplier', 'back_url': 'supplier_list'})

# Stock Transactions (In / Out)
@login_required
def transaction_list(request):
    transactions = StockTransaction.objects.all().order_by('-date')
    return render(request, 'inventory/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            product = transaction.product
            
            # Normal Django view logic for updating stock
            if transaction.transaction_type == 'IN':
                product.quantity += transaction.quantity
            elif transaction.transaction_type == 'OUT':
                product.quantity -= transaction.quantity
                
            product.save()
            transaction.save()
            messages.success(request, f'Stock {transaction.transaction_type} recorded successfully.')
            return redirect('transaction_list')
    else:
        form = StockTransactionForm()
    return render(request, 'inventory/form.html', {'form': form, 'title': 'New Stock Transaction', 'back_url': 'transaction_list'})


# --- API Views ---

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class StockTransactionViewSet(viewsets.ModelViewSet):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        transaction = serializer.save()
        product = transaction.product
        
        if transaction.transaction_type == 'IN':
            product.quantity += transaction.quantity
        elif transaction.transaction_type == 'OUT':
            product.quantity -= transaction.quantity
            
        product.save()
