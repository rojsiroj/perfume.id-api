"""
    app URL Configuration
"""

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="api/docs")),
    path("admin/", admin.site.urls),
    path("api/schema", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("api/user/", include("user.urls")),
    path("api/product/", include("product.urls")),
    path("", include("django_prometheus.urls")),
]
