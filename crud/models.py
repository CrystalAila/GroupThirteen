from django.db import models

class Category(models.Model):
    class Meta:
        db_table = 'tbl_categories'

    category_id = models.BigAutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    class Meta:
        db_table = 'tbl_products'

    product_image = models.ImageField(null=True, default='', blank=True, upload_to='products/')
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity_in_stock = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    units_sold = models.IntegerField(default=0)
    stock_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

class Transaction(models.Model):
    class Meta:
        db_table = 'tbl_transactions'

    transaction_id = models.BigAutoField(primary_key=True)
    cashier_name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction {self.transaction_id} - {self.cashier_name}'


class TransactionItem(models.Model):
    class Meta:
        db_table = 'tbl_transaction_items'

    item_id = models.BigAutoField(primary_key=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.product_name} x {self.quantity}'
