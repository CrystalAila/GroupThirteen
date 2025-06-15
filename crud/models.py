from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone

class Role(models.Model):
    ROLE_CHOICES = [
        ('Cashier', 'Cashier'),
        ('Manager', 'Manager'),
    ]
    
    class Meta:
        db_table = 'tbl_roles'
    
    role_id = models.BigAutoField(primary_key=True)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_type

class CustomUserManager(UserManager):
    def _create_user(self, username, email, full_name, password, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("You have not provided a valid email address")
        if not full_name:
            raise ValueError("Full name is required")
        if not password:
            raise ValueError("Password is required!")
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            full_name=full_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, full_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, full_name, password, **extra_fields)

    def create_superuser(self, username, email, full_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, full_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)  # Removed default=1
    profile = models.ImageField(null=True, blank=True, upload_to='profiles/')
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'full_name']

    class Meta:
        db_table = 'tbl_users'

    def get_full_name(self):
        return self.full_name

    def __str__(self):
        return self.username

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    minimum_stock = models.IntegerField(default=5)

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

    def change(self):
        return self.amount_paid - self.total_amount


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
