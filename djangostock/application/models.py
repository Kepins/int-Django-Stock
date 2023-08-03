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

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    # REQUIRED_FIELDS must contain all required fields on your user model,
    # but should not contain the USERNAME_FIELD or password as these fields will always be prompted for.
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email
