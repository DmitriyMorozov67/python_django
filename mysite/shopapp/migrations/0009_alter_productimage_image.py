# Generated by Django 4.2.5 on 2023-09-22 14:08

from django.db import migrations, models
import shopapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0008_order_receipt_product_preview_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(null=True, upload_to=shopapp.models.product_images_directory_path),
        ),
    ]