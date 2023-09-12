from timeit import default_timer

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from .forms import GroupForm
from .forms_model import ProductForm, OrderForm
from .models import Product, Order

class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('laptop', 1999),
            ('desktop', 2999),
            ('smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
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
    model = Product
    context_object_name = "product"
class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    #model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)
class ProductCreateView(UserPassesTestMixin, CreateView):

    model = Product
    fields = "name", "price", "description", "discount", "created_by"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.create_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.has_perm('shopapp.add_product')



@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser or u.has_perm('shopapp.change_product')), name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    fields = "name", "price", "description", "discount", "created_by"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)

        if not queryset.filter(pk=self.kwargs['pk'], created_by=self.request.user).exists():
            raise Http404("You do not have access to this product.")
        return queryset

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
