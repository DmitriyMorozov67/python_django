import json
from string import ascii_letters
from random import choices

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


# Create your tests here.
class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(

            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "A good table",
                "discount": "10",
                # "create_by": "admin",
            },
            HTTP_USER_AGENT="Mozilla/5.0",
        )

        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objecs.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best Product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="bob", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:order_list"), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:order_list"), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_get_product_view(self):
        response = self.client.get(
            reverse("shopapp:products-export"),
            HTTP_USER_AGENT="Mozilla/5.0",
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="Bob", password="qwerty")
        permission_order = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission_order)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address='ul Bacunina, d 10',
            promocode='SALE_123',
            user=self.user,
        )

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_detail_view(self):
        response = self.client.get(reverse(
            "shopapp:order_details",
            kwargs={
                "pk": self.order.pk
            }),
            HTTP_USER_AGENT="Mozzilla/5.0",
        )
        expected_data = self.order.pk
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["order"].pk, expected_data)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "users-fixture.json",
        "products-fixture.json",
        "orders-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser', password='testpassword', is_staff=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_export(self):
        response = (self.client.get(
            reverse('shopapp:orders-export'),
            HTTP_USER_AGENT="Mozilla/5.0"
        ))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.all()
        expected_data = [
                {
                    'order_id': order.id,
                    'delivery_address': order.delivery_address,
                    'promocode': order.promocode,
                    'user_id': order.user_id,
                    'product_ids': [product.pk for product in order.products.all()],
                }
                for order in orders
            ]

        orders_data = response.json()
        self.assertEqual(orders_data['orders'], expected_data)
