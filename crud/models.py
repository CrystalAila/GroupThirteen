from django.db import models

# Create your models here.

class Categories(models.Model):
    class Meta:
        db_table = 'tbl_categories'

    category_id = models.BigAutoField(primary_key=True, blank=False)  # category_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
    category_name = models.CharField(max_length=100, blank=False)  # category_name VARCHAR(100) NOT NULL
    created_at = models.DateTimeField(auto_now_add=True)  # created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    updated_at = models.DateTimeField(auto_now=True)  # updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

class Products(models.Model):
    class Meta:
        db_table = 'tbl_products'
    
    product_id = models.BigAutoField(primary_key=True, blank=False)  # product_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
    product_name = models.CharField(max_length=100, blank=False)  # product_name VARCHAR(100) NOT NULL
    stock_status = models.BooleanField(default=True)  # stock_status BOOLEAN NOT NULL DEFAULT True
    categories = models.ForeignKey(Categories, on_delete=models.CASCADE)  # category_id BIGINT NOT NULL
    quantity_in_stock = models.IntegerField(blank=False)  # quantity_in_stock INT NOT NULL
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)  # purchase_price DECIMAL(10,2) NOT NULL
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)  # selling_price DECIMAL(10,2) NOT NULL
    created_at = models.DateTimeField(auto_now_add=True)  # created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    updated_at = models.DateTimeField(auto_now=True)  # updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP