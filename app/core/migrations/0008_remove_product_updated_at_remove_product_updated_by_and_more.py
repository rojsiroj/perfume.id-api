# Generated by Django 4.0.10 on 2024-08-08 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_product_stock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='product',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='productstock',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='productstock',
            name='updated_by',
        ),
    ]
