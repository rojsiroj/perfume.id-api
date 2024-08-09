"""
Database core models
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django_prometheus.models import ExportModelOperationsMixin


class UserManager(BaseUserManager):
    # Manager for users

    def create_user(self, email, password=None, **extra_fields):
        # Create, save and return a new user
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        # Create, save and return a new superuser
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # User in the system
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Product(ExportModelOperationsMixin("product"), models.Model):
    # Product object
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_created_by",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=0)
    categories = models.ManyToManyField("ProductCategory")
    stock = models.OneToOneField(
        "ProductStock",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="product_stock",
    )

    def __str__(self):
        return self.name

    def stock_count(self):
        try:
            product_stock = ProductStock.objects.get(product=self.pk)
            return product_stock.quantity
        except ProductStock.DoesNotExist:
            return 0


class ProductCategory(
    ExportModelOperationsMixin("product_category"), models.Model
):
    # Product category object
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_category_created_by",
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductStock(
    ExportModelOperationsMixin("product_category"), models.Model
):
    # Product stock object
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_stock_created_by",
    )
    product = models.OneToOneField(
        "Product",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="product_stock",
    )
    quantity = models.IntegerField()

    def __str__(self):
        return self.product.name
