from django.contrib import admin
from .models import Product, Transaction, TransactionItem

# Register your models here.
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(TransactionItem)