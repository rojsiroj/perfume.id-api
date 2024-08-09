from rest_framework import serializers

from core.helper import DEFAULT_READ_ONLY_FIELDS
from core.models import Product, ProductCategory, ProductStock


class ProductCategorySerializer(serializers.ModelSerializer):
    # Serializer for the product category object
    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "created_at",
            "created_by",
        ]
        read_only_fields = DEFAULT_READ_ONLY_FIELDS


class ProductStockSerializer(serializers.ModelSerializer):
    # Serializer for the product stock object
    class Meta:
        model = ProductStock
        fields = [
            "id",
            "product",
            "quantity",
            "created_at",
            "created_by",
        ]
        read_only_fields = DEFAULT_READ_ONLY_FIELDS


class ProductSerializer(serializers.ModelSerializer):
    # Serializer for the product object
    categories = ProductCategorySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "categories",
            "stock_count",
            "created_at",
            "created_by",
        ]
        read_only_fields = DEFAULT_READ_ONLY_FIELDS + ["stock_count"]

    def _get_or_create_categories(self, categories, product):
        # Handle getting or creating categories as needed
        auth_user = self.context["request"].user
        for category in categories:
            category_obj, _ = ProductCategory.objects.get_or_create(
                created_by=auth_user,
                **category,
            )
            product.categories.add(category_obj)

    def create(self, validated_data):
        # Create and return a new product
        categories = validated_data.pop("categories", [])
        product = Product.objects.create(**validated_data)
        self._get_or_create_categories(categories, product)

        return product

    def update(self, instance, validated_data):
        # Update an existing product
        categories = validated_data.pop("categories", None)

        if categories is not None:
            instance.categories.clear()
            self._get_or_create_categories(categories, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProductDetailSerializer(ProductSerializer):
    # Serializer for product detail view
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["description"]
