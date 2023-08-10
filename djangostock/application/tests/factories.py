import string

import factory
import factory.random
from django.utils import timezone
from djangostock.application.models import User, Stock, Currency, Country, StockTimeSeries


def setup_test_environment():
    factory.random.reseed_random("my_seed")


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda a: "{}.{}@example.com".format(a.first_name, a.last_name).lower())
    create_date = factory.LazyFunction(timezone.now)
    modify_date = factory.LazyFunction(timezone.now)
    is_active = True
    is_admin = False


def _symbol(n):
    """
    Generates symbols in this pattern:
    "AAAA" for n = 0, "AAAB" for n = 1,... and so on
    """
    LETTERS = list(string.ascii_uppercase)
    SYMBOL_LENGTH = 4

    symbol = ""
    for i in range(SYMBOL_LENGTH - 1, -1, -1):
        new_letter = LETTERS[n // len(LETTERS) ** i % len(LETTERS)]
        symbol += new_letter
    return symbol


class StockFactory(factory.Factory):
    class Meta:
        model = Stock

    name = factory.Sequence(lambda n: f"Name of Stock {_symbol(n)}")
    symbol = factory.Sequence(lambda n: _symbol(n))
    exchange_name = "NASDAQ"
    type_of_stock = "Common Stock"
    last_update_date = None
    currency = Currency.objects.get(name="USD")
    country = Country.objects.get(name="United States")


class StockTimeSeriesFactory(factory.Factory):
    class Meta:
        model = StockTimeSeries

    open = 2.55
    close = 2.12
    high = 2.60
    low = 2.08
    volume = 6600
