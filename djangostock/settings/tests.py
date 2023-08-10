# flake8: noqa

from .base import *

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


CELERY_TASK_ALWAYS_EAGER = True
