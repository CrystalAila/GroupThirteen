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

    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity_in_stock = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name
