from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product, ProductCategory
from product import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "categories",
                OpenApiTypes.STR,
                description="Comma separated list of categories to filter",
            ),
        ]
    )
)
class ProductViewSet(viewsets.ModelViewSet):
    # View for manage product APIs
    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        # Convert a list of strings to integers
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        # Retrieve products for authenticated user
        categories = self.request.query_params.get("categories")
        queryset = self.queryset
        if categories:
            tag_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=tag_ids)

        return (
            queryset.filter(created_by=self.request.user)
            .order_by("-id")
            .distinct()
        )

    def get_serializer_class(self):
        # Return the serializer class for request
        if self.action == "list":
            return serializers.ProductSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new product
        serializer.save(created_by=self.request.user)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned_only",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Filter by item assigned to products",
            )
        ]
    )
)
class ProductCategoryViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    # View for manage categorie APIs
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve categories for authenticated user
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(product__isnull=False)
        return (
            queryset.filter(created_by=self.request.user)
            .order_by("-name")
            .distinct()
        )

    serializer_class = serializers.ProductCategorySerializer
    queryset = ProductCategory.objects.all()
