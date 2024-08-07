"""
Test for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models
from core.helper import create_user, get_time_in_utc


def create_product_category():
    user = create_user()
    product_category = models.ProductCategory.objects.create(
        created_at=get_time_in_utc(),
        created_by=user,
        name="Category1",
    )

    return product_category


def create_product():
    user = create_user()
    product = models.Product.objects.create(
        created_at=get_time_in_utc(),
        created_by=user,
        name="Sample product name",
        description="Sample recipe description.",
        price=15000,
    )
    return product


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        # Test create user with email
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test email is normalized for new users
        sample_emails = [
            [
                "test1@EXAMPLE.com",
                "test1@example.com",
            ],
            [
                "Test2@Example.com",
                "Test2@example.com",
            ],
            [
                "TEST3@EXAMPLE.COM",
                "TEST3@example.com",
            ],
            [
                "test4@example.COM",
                "test4@example.com",
            ],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email,
                "sample123",
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        # Test that creating a user without an email raises a ValueError
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                "",
                "test123",
            )

    def test_create_superuser(self):
        # Test creating superuser
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_category(self):
        # Test creating a product category is successful
        product_category = create_product_category()
        self.assertEqual(str(product_category), product_category.name)

    def test_create_product(self):
        # Test creating a product is successful
        product_category = create_product_category()
        product = create_product()
        product.categories.add(product_category)

        self.assertEqual(str(product), product.name)

    def test_create_stock(self):
        # Test creating a product category is successful
        user = create_user()
        product = create_product()
        product_stock = models.ProductStock.objects.create(
            created_at=get_time_in_utc(),
            created_by=user,
            product=product,
            quantity=10,
        )

        self.assertEqual(str(product_stock), product.name)
        self.assertEqual(product_stock.quantity, 10)
