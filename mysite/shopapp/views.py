"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""
import logging
from timeit import default_timer
from csv import DictWriter

from django.contrib.auth.models import Group
from django.contrib.syndication.views import Feed
from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseRedirect,
    JsonResponse
)
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .common import save_csv_products, save_csv_orders
from .forms import GroupForm, ProductForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer

log = logging.getLogger(__name__)

@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущностей товара.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]
    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):

        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}-export.csv"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(
                description="Empty response, product by id not found"
            ),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    """
    Набор представлений для действий над Order.

    Полный CRUD для сущностей заказа.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = [
        "user",
        "delivery_address",
        "products",
        "promocode",
    ]
    ordering_fields = [
        "user",
        "delivery_address",
        "products",
    ]

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}-export.csv"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "user",
            "delivery_address",
            "products",
            "promocode",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for order in queryset:
            writer.writerow({
                field: getattr(order, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        orders = save_csv_orders(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


@action(
    detail=False,
    methods=["post"],
    parser_classes=[MultiPartParser],
)
def upload_csv(self, request: Request):
    products = save_csv_products(
        request.FILES["file"].file,
        encoding=request.encoding,
    )
    serializer = self.get_serializer(products, many=True)
    return Response(serializer.data)


class ShopIndexView(View):
    """
    Набор представлений для действий над ShopIndex.

    Вывод приветсвия и информации.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('laptop', 1999),
            ('desktop', 2999),
            ('smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 5,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),

        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/product-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'shopapp.add_product'
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")
    form_class = ProductForm

    def form_valid(self, form):
        form.instance.create_by = self.request.user
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductUpdateView(UpdateView, UserPassesTestMixin):
    model = Product
    # fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def test_func(self):
        product = self.get_object()
        return self.request.user.is_superuser or (
                self.request.user == product.created_by
                or self.request.user.has_perm('shopapp.change_product')
        )

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class CreateOrderView(CreateView):
    model = Order
    fields = "user", "delivery_address", "promocode", "products"
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateForm(UpdateView):
    model = Order
    fields = "user", "delivery_address", "promocode", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:order_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        elem = products_data[0]
        name = elem["name"]
        print("name:", name)
        return JsonResponse({"products": products_data})


class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        orders = Order.objects.all()
        orders_data = [
            {
                "order_id": order.id,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.id,
                "product_ids": [product.id for product in order.products.all()]
            }
            for order in orders
        ]

        return JsonResponse({'orders': orders_data})


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = "Updates on changes and addition products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.prefetch_related("images")
        # (
    #     Product.objects
    #     .select_related("author")
    #     .prefetch_related("tags")
    #     .order_by("-pub_date")[:5]
    #     .defer("content")
    # )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]