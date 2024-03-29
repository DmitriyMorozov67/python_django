# Generated by Django 4.2.5 on 2023-09-22 09:47

from django.db import migrations, models
import django.db.models.deletion
import shopapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0007_alter_product_options_product_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='receipt',
            field=models.FileField(null=True, upload_to='orders/receipt/'),
        ),
        migrations.AddField(
            model_name='product',
            name='preview',
            field=models.ImageField(blank=True, null=True, upload_to=shopapp.models.product_preview_directory_path),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=shopapp.models.product_images_directory_path)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='shopapp.product')),
            ],
        ),
    ]
