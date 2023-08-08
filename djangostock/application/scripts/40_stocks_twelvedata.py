import os
import sys
import random
from pathlib import Path

import django
import requests


sys.path.append(Path(__file__).parent.parent.parent.parent.as_posix())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangostock.settings.local")
django.setup()

from djangostock.application.serializers import StockSerializer

query_params = {
    "currency": "USD",
    "country": "United States",
    "exchange": "NASDAQ",
    "type": "Common Stock",
}


r = requests.get(
    "https://api.twelvedata.com/stocks",
    params=query_params,
)
stocks = random.sample(r.json()["data"], 40)

for stock in stocks:
    serializer = StockSerializer(data=stock)
    if serializer.is_valid():
        serializer.save()
