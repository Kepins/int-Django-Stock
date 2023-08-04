import factory
import factory.random
import pytz
from django.utils import timezone
from djangostock.application.models import User


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
