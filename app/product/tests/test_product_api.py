from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, ProductCategory
from core.helper import create_user, get_time_in_utc

from product.serializers import ProductDetailSerializer, ProductSerializer

PRODUCTS_URL = reverse("product:product-list")


def detail_url(product_id):
    # Create and return a product detail URL
    return reverse("product:product-detail", args=[product_id])


def create_product(created_by, **params):
    # Create and return a sample product
    defaults = {
        "name": "Sample product name",
        "description": "Sample product description",
        "created_at": get_time_in_utc(),
        "price": 15000,
    }
    defaults.update(params)

    product = Product.objects.create(
        created_by=created_by,
        **defaults,
    )
    return product


class PublicProductAPITests(TestCase):
    # Test unauthenticated product API requests

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test auth is required to call API
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductAPITests(TestCase):
    # Test authenticated product API requests
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_products(self):
        # Test retrieving a list of products
        create_product(created_by=self.user)
        create_product(created_by=self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.all().order_by("-id")
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_product_list_limited_to_user(self):
        # Test list of products is limited to authenticated user
        other_user = create_user(
            email="other@example.com",
            password="password123",
        )
        create_product(created_by=other_user)
        create_product(created_by=self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.filter(created_by=self.user)
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_product_detail(self):
        # Test get product detail
        product = create_product(created_by=self.user)

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        # Test creating a product
        payload = {
            "name": "Sample product name",
            "description": "Sample product description",
            "price": 15000,
            "created_by": self.user,
        }
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        product = Product.objects.get(id=res.data["id"])
        for key, value in payload.items():
            self.assertEqual(getattr(product, key), value)
        self.assertEqual(product.created_by, self.user)

    def test_partial_update_product(self):
        # Test partial update of a product
        description = "Sample product description"
        product = create_product(
            created_by=self.user,
            name="Sample product name",
            description=description,
        )

        payload = {
            "name": "New product name",
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        self.assertEqual(product.name, payload["name"])
        self.assertEqual(product.description, description)
        self.assertEqual(product.created_by, self.user)

    def test_full_update_product(self):
        # Test full update of a product
        product = create_product(created_by=self.user)

        payload = {
            "name": "Sample product name",
            "description": "Sample product description",
            "price": 15000,
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(product, key), value)
        self.assertEqual(product.created_by, self.user)

    def test_update_user_returns_error(self):
        # Test changing the product user results is an error
        new_user = create_user(email="user2@example.com", password="test123")
        product = create_product(created_by=self.user)

        payload = {"created_by": new_user}
        url = detail_url(product.id)
        self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.created_by, self.user)

    def test_delete_product(self):
        # Test deleting a product successful
        product = create_product(created_by=self.user)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_delete_product_other_users_product_error(self):
        # Test trying to delete another users product gives error
        new_user = create_user(email="user2@example.com", password="test123")
        product = create_product(created_by=new_user)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(id=product.id).exists())

    def test_create_product_with_new_categories(self):
        # Test creating a product with new categories
        payload = {
            "name": "Sample product name",
            "description": "Sample product description",
            "price": 15000,
            "categories": [{"name": "For Men"}, {"name": "For Women"}],
        }
        res = self.client.post(PRODUCTS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        products = Product.objects.filter(created_by=self.user)
        self.assertEqual(products.count(), 1)

        product = products[0]
        self.assertEqual(product.categories.count(), 2)

        for category in payload["categories"]:
            exists = product.categories.filter(
                name=category["name"],
                created_by=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_product_with_existing_categories(self):
        # Test creating a product with existing categories
        category1 = ProductCategory.objects.create(
            created_at=get_time_in_utc(),
            created_by=self.user,
            name="Unisex",
        )
        payload = {
            "name": "Sample product name",
            "description": "Sample product description",
            "price": 15000,
            "categories": [{"name": category1.name}, {"name": "Women"}],
        }

        res = self.client.post(PRODUCTS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        products = Product.objects.filter(created_by=self.user)
        self.assertEqual(products.count(), 1)

        product = products[0]
        self.assertEqual(product.categories.count(), 2)
        self.assertIn(category1, product.categories.all())

        for category in payload["categories"]:
            exists = product.categories.filter(
                name=category["name"],
                created_by=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_category_on_update(self):
        # Test creating a category on update
        product = create_product(created_by=self.user)
        payload = {
            "categories": [{"name": "Unisex"}],
        }

        url = detail_url(product.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        self.assertEqual(product.categories.count(), 1)

        new_category = ProductCategory.objects.get(
            created_by=self.user, name="Unisex"
        )
        self.assertIn(new_category, product.categories.all())

    def test_update_product_assign_task(self):
        # Test updating a product with existing categories
        category1 = ProductCategory.objects.create(
            created_at=get_time_in_utc(),
            created_by=self.user,
            name="Unisex",
        )
        product = create_product(created_by=self.user)
        product.categories.add(category1)

        category2 = ProductCategory.objects.create(
            created_at=get_time_in_utc(),
            created_by=self.user,
            name="Men",
        )
        payload = {
            "categories": [{"name": category2.name}],
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        self.assertEqual(product.categories.count(), 1)
        self.assertIn(category2, product.categories.all())
        self.assertNotIn(category1, product.categories.all())

    def test_clear_product_categories(self):
        # Test clearing product categories
        category1 = ProductCategory.objects.create(
            created_at=get_time_in_utc(),
            created_by=self.user,
            name="Unisex",
        )
        product = create_product(created_by=self.user)
        product.categories.add(category1)

        payload = {
            "categories": [],
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        self.assertEqual(product.categories.count(), 0)
        self.assertNotIn(category1, product.categories.all())

    def test_filter_product_by_categories(self):
        # Test returning products with specific categories
        product1 = create_product(created_by=self.user, name="Product 1")
        product2 = create_product(created_by=self.user, name="Product 2")
        category1 = ProductCategory.objects.create(
            created_at=get_time_in_utc(),
            created_by=self.user,
            name="Women",
        )
        category2 = ProductCategory.objects.create(
            created_at=get_time_in_utc(),
            created_by=self.user,
            name="Men",
        )
        product1.categories.add(category1)
        product2.categories.add(category2)
        product3 = create_product(created_by=self.user, name="Product 3")

        params = {"categories": f"{category1.id},{category2.id}"}
        res = self.client.get(PRODUCTS_URL, params)

        serializer1 = ProductSerializer(product1)
        serializer2 = ProductSerializer(product2)
        serializer3 = ProductSerializer(product3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
