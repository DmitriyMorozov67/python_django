from csv import DictReader
from io import TextIOWrapper

from .models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products

def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    orders = []
    for row in reader:
        product_ids = row.pop('product_ids').split(',')
        order = Order.objects.create(**row)
        products = Product.objects.filter(id__in=product_ids)
        order.products.set(products)
    orders.append(order)

    return order