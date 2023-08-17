#!/bin/bash

# Run migrations
python manage.py migrate
# Run daphne server
daphne djangostock.asgi:application -b 0.0.0.0 -p 8000
