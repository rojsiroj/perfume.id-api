"""
Test for product stock APIs
"""

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import ProductStock, Product
from core.helper import create_user, get_time_in_utc

from product.serializers import ProductStockSerializer

PRODUCT_STOCKS_URL = reverse("product:productstock-list")


def detail_url(stock_id):
    # Return stock detail URL
    return reverse("product:productstock-detail", args=[stock_id])


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


class PublicProductStockAPITests(TestCase):
    # Test unauthenticated stock API requests

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test auth is required for retrieving stocks
        res = self.client.get(PRODUCT_STOCKS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductStockAPITests(TestCase):
    # Test authenticated stock API requests

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_stocks(self):
        # Test retrieving a list of stocks
        product = create_product(
            created_by=self.user,
            name="Sample product name",
        )
        product2 = create_product(
            created_by=self.user,
            name="Sample product name 2",
        )

        ProductStock.objects.create(
            created_by=self.user, product=product, quantity=10
        )
        ProductStock.objects.create(
            created_by=self.user, product=product2, quantity=1
        )

        res = self.client.get(PRODUCT_STOCKS_URL)

        stocks = ProductStock.objects.all().order_by("-quantity")
        serializer = ProductStockSerializer(stocks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_stocks_limited_to_user(self):
        # Test list of stocks is limited to auntheticated user
        product = create_product(
            created_by=self.user,
            name="Sample product name",
        )
        product2 = create_product(
            created_by=self.user,
            name="Sample product name 2",
        )

        other_user = create_user(email="user2@example.com")

        ProductStock.objects.create(
            created_by=other_user,
            product=product,
            quantity=10,
        )

        stock = ProductStock.objects.create(
            created_by=self.user,
            product=product2,
            quantity=1,
        )

        res = self.client.get(PRODUCT_STOCKS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["quantity"], stock.quantity)
        self.assertEqual(res.data[0]["id"], stock.id)

    def test_update_stock(self):
        # Test updating a stock
        product = create_product(
            created_by=self.user,
            name="Sample product name",
        )

        stock = ProductStock.objects.create(
            created_by=self.user,
            product=product,
            quantity=10,
        )
        payload = {"quantity": 100}

        url = detail_url(stock.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        stock.refresh_from_db()
        self.assertEqual(stock.quantity, payload["quantity"])

    def test_delete_stock(self):
        # Test deleting a stock
        product = create_product(
            created_by=self.user,
            name="Sample product name",
        )
        stock = ProductStock.objects.create(
            created_by=self.user,
            product=product,
            quantity=10,
        )

        url = detail_url(stock.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        stocks = ProductStock.objects.filter(created_by=self.user)
        self.assertFalse(stocks.exists())
