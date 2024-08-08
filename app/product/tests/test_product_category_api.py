"""
Test for product category APIs
"""

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import ProductCategory, Product
from core.helper import create_user, get_time_in_utc

from product.serializers import ProductCategorySerializer

PRODUCT_CATEGORIES_URL = reverse("product:productcategory-list")


def detail_url(category_id):
    # Return category detail URL
    return reverse("product:productcategory-detail", args=[category_id])


class PublicProductCategoryAPITests(TestCase):
    # Test unauthenticated category API requests

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test auth is required for retrieving categories
        res = self.client.get(PRODUCT_CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductCategoryAPITests(TestCase):
    # Test authenticated category API requests

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_categories(self):
        # Test retrieving a list of categories
        ProductCategory.objects.create(created_by=self.user, name="Men")
        ProductCategory.objects.create(created_by=self.user, name="Women")

        res = self.client.get(PRODUCT_CATEGORIES_URL)

        categories = ProductCategory.objects.all().order_by("-name")
        serializer = ProductCategorySerializer(categories, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_user(self):
        # Test list of categories is limited to auntheticated user
        other_user = create_user(email="user2@example.com")
        ProductCategory.objects.create(created_by=other_user, name="Men")
        category = ProductCategory.objects.create(
            created_by=self.user,
            name="Women",
        )

        res = self.client.get(PRODUCT_CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], category.name)
        self.assertEqual(res.data[0]["id"], category.id)

    def test_update_category(self):
        # Test updating a category
        category = ProductCategory.objects.create(
            created_by=self.user, name="Men"
        )
        payload = {"name": "Women"}

        url = detail_url(category.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        category.refresh_from_db()
        self.assertEqual(category.name, payload["name"])

    def test_delete_category(self):
        # Test deleting a category
        category = ProductCategory.objects.create(
            created_by=self.user, name="Men"
        )

        url = detail_url(category.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        categories = ProductCategory.objects.filter(created_by=self.user)
        self.assertFalse(categories.exists())

    def test_filter_category_assigned_to_products(self):
        # Test listing categories to those assigned to products
        category1 = ProductCategory.objects.create(
            created_by=self.user, name="Men"
        )
        category2 = ProductCategory.objects.create(
            created_by=self.user, name="Women"
        )
        product = Product.objects.create(
            created_by=self.user,
            created_at=get_time_in_utc(),
            name="Sample product name",
            description="Sample product description",
            price=15000,
        )
        product.categories.add(category1)

        res = self.client.get(PRODUCT_CATEGORIES_URL, {"assigned_only": 1})

        serializer1 = ProductCategorySerializer(category1)
        serializer2 = ProductCategorySerializer(category2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_test_unique(self):
        # Test filtered categories returns a unique list
        category = ProductCategory.objects.create(
            created_by=self.user, name="Men"
        )
        ProductCategory.objects.create(created_by=self.user, name="Women")

        product1 = Product.objects.create(
            created_by=self.user,
            created_at=get_time_in_utc(),
            name="Sample product name",
            description="Sample product description",
            price=15000,
        )
        product2 = Product.objects.create(
            created_by=self.user,
            created_at=get_time_in_utc(),
            name="Sample product name 2",
            description="Sample product description 2",
            price=15000,
        )
        product1.categories.add(category)
        product2.categories.add(category)

        res = self.client.get(PRODUCT_CATEGORIES_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data), 1)
