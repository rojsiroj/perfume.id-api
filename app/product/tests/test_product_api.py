from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product
from core.helper import create_user, get_time_in_utc

PRODUCTS_URL = reverse("product:product-list")


def create_product(user, **params):
    # Create and return a sample product
    defaults = {
        "name": "Sample product name",
        "description": "Sample product description",
        "created_at": get_time_in_utc(),
        "price": 15000,
    }
    defaults.update(params)

    product = Product.objects.create(
        created_by=user,
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
