from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from online_sales.settings import EMAIL_HOST_USER


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product', blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.name


# class Order(models.Model):
#     CREATED_TYPE = 1
#     STATUS_COLORS = (
#         (CREATED_TYPE, '#0022FF'),
#     )
#     STATUS_TYPES = (
#         (CREATED_TYPE, 'Created'),
#     )
#     status = models.PositiveSmallIntegerField(default=CREATED_TYPE)
#     price = models.DecimalField(max_digits=9, decimal_places=2)
#     start_datetime = models.DateTimeField(default=timezone.now)


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['date_added']
        db_table = 'Cart'

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'CartItem'

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product

    def accept(self):
        self.accept_datetime = timezone.now()
        self.save()
        html = render_to_string('emails/accept_email.html', {'cart': self,
                                                             'user': User})
        plain_message = strip_tags(html)
        send_mail('order accepted', plain_message, EMAIL_HOST_USER, (User.email,), html_message=html)
