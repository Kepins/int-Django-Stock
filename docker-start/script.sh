#!/bin/bash

# Run migrations
python manage.py collectstatic --no-input
python manage.py migrate
python djangostock/application/scripts/40_stocks_twelvedata.py
python djangostock/application/scripts/start_periodic_tasks.py
# Run daphne server
daphne djangostock.asgi:application -b 0.0.0.0 -p 8000
