"""
URL Mappings for the product API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from product import views

app_name = "product"

router = DefaultRouter()
router.register("products", views.ProductViewSet)
router.register("categories", views.ProductCategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
