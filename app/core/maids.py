"""
Maids for miscellaneous purposes
"""

from core.models import User, Product, ProductCategory, ProductStock
from core.helper import create_user
from random import randint


def db_seed(with_deletion=False, total_data=10):
    """
    Seed the database with initial data
    """
    if with_deletion:
        User.objects.all().delete()
        ProductStock.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()

    # Create a user
    user = create_user(email="ecommerce@example.com", password="admin")

    try:
        # Create product categories
        categories = []
        for i in range(total_data):
            categories.append(
                ProductCategory(
                    created_by=user,
                    name=f"Category {i}",
                )
            )

        ProductCategory.objects.bulk_create(categories)

        print(f"Success create {total_data} product categories")
    except Exception as e:
        print("Product categories bulk create failed:", str(e))

    try:
        # Create products
        product_categories = ProductCategory.objects.all()

        products = []
        for i in range(total_data):
            product = Product(
                created_by=user,
                name=f"Product {i}",
                price=randint(1000, 100000),
                description=f"lorem ipsum dolor sit amet, consectetur adipiscing elit in  auctor elit et just eu just product  consectetur adipiscing elit in  auctor elit et just eu just product  consectetur adipiscing elit in  auctor elit et just eu just product  consectetur adipiscing elit in  auctor elit et just eu just product {i} description ",
            )
            product.save()

            product.categories.add(
                product_categories[randint(0, len(product_categories) - 1)]
            )
            product.save()

        print(f"Success create {total_data} products")
    except Exception as e:
        print("Product bulk create failed:", str(e))

    try:
        # Create product stocks
        products = Product.objects.all()

        stocks = []
        for product in products:
            stocks.append(
                ProductStock(
                    created_by=user,
                    product=product,
                    quantity=randint(0, 1000),
                )
            )

        ProductStock.objects.bulk_create(stocks)

        print(f"Success create {len(products)} product stocks")
    except Exception as e:
        print("Product Stock bulk create failed:", str(e))
