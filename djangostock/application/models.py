from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from .managers import UserManager


class ModelWithTimestamps(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, ModelWithTimestamps):
    first_name = models.fields.CharField(max_length=40)
    last_name = models.fields.CharField(max_length=40)
    email = models.fields.EmailField(unique=True)
    is_admin = models.fields.BooleanField(default=False)
    is_active = models.fields.BooleanField(default=True)

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    # REQUIRED_FIELDS must contain all required fields on your user model,
    # but should not contain the USERNAME_FIELD or password as these fields will always be prompted for.
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email


class Currency(models.Model):
    name = models.fields.CharField(max_length=40)


class Country(models.Model):
    name = models.fields.CharField(max_length=100)


class Stock(models.Model):
    class TypeOfStock(models.TextChoices):
        COMMON_STOCK = "Common Stock"

    name = models.fields.CharField(max_length=250)
    symbol = models.fields.CharField(max_length=40)
    exchange_name = models.fields.CharField(max_length=40)
    type_of_stock = models.fields.CharField(max_length=100, choices=TypeOfStock.choices)
    last_update_date = models.DateTimeField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)


class StockTimeSeries(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    open = models.fields.FloatField()
    close = models.fields.FloatField()
    high = models.fields.FloatField()
    low = models.fields.FloatField()
    volume = models.fields.IntegerField()
    recorded_date = models.DateTimeField()
