# Generated by Django 4.2.5 on 2023-10-09 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0009_alter_productimage_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name', 'price'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterField(
            model_name='order',
            name='receipt',
            field=models.FileField(blank=True, null=True, upload_to='orders/receipt/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]