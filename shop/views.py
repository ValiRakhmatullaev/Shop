from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group, User
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
# Create your views here.
from shop.models import Category, Product, Cart, CartItem
from .serializers import ProductSerializer
from django.core.mail import send_mail


# class CreateOrderView(FormView):
#     template_name = 'create_order.html'
#     form_class = CreateOrderForm
#     success_url = reverse_lazy('list_my_orders')
#     extra_context = {'title': 'Create order'}
#
#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         return form
#
#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.save()
#         form.save_m2m()
#         return super().form_valid(form)


# class ListMyOrdersView(ListView):
#     template_name = 'list_my_orders.html'
#     extra_context = {'title': 'List my orders', 'order_model': Order}
#     ordering = '-start_datetime'

# def get_queryset(self):
#     user = self.request.user
#     return Order.objects.filter()
#
# def order_history(request, username):
#     order_qs = Order.objects.filter(user__username=username)
#
#     context = {
#         'order_qs': order_qs,
#     }
#     return render(request, 'list_my_orders.html', context)


# class ProductAPIView(APIView):
#     def get(self, request):
#         w = Product.objects.all().values()
#         return Response({'posts': ProductSerializer(w, many=True).data})
#
#     def post(self, request):
#         new_post = Product.objects.create(
#             name=request.data['name'],
#             category=request.data['category'],
#             description=request.data['description'],
#             slug=request.data['slug'],
#             price=request.data['price'],
#             stock=request.data['stock'],
#             available=request.data['available'],
#             created=request.data['created'],
#             updated=request.data['updated']
#
#         )
#         return Response({'post': model_to_dict(new_post)})


#
# class Home(ListView):
#     model = Category
#     template_name = 'home.html'


def home(request, category_slug=None):
    category_page = None
    products = None
    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category_page, available=True)
    else:
        products = Product.objects.all().filter(available=True)
    return render(request, 'home.html', {'category': category_page, 'products': products})


def product(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    return render(request, 'product.html', {'product': product})


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()

    return redirect('cart_detail')


def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter))


def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')


def cart_remove_product(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail')


def signUpView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            user_group = Group.objects.get(name='User')
            user_group.user_set.add(signup_user)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def loginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('signup')

    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logoutView(request):
    logout(request)
    return redirect('login')
