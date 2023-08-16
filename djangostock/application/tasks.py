import datetime

import requests
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings

from djangostock.application.models import Stock

from djangostock.application.serializers import StockTimeSeriesSerializer, StockSerializer


@shared_task(ignore_result=True)
def update_time_series(symbol):
    query_params = {
        "symbol": symbol,
        "apikey": settings.API_KEY_TWELVEDATA,
        "interval": "1day",
    }

    r = requests.get(
        "https://api.twelvedata.com/time_series",
        params=query_params,
    )
    if r.status_code == 200 and r.json()["status"] == "ok":
        updated = False
        stock = Stock.objects.get(symbol=symbol)
        if not stock.last_update_date:
            stock.last_update_date = r.json()["values"][0]["datetime"]
            for value in r.json()["values"]:
                data = value
                data["stock"] = stock.pk
                serializer = StockTimeSeriesSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
            stock.save()
            updated = True
        else:
            values = [
                v
                for v in r.json()["values"]
                if datetime.datetime.strptime(v["datetime"], "%Y-%m-%d").date() > stock.last_update_date
            ]
            for value in values:
                data = value
                data["stock"] = stock.pk
                serializer = StockTimeSeriesSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
            if values:
                stock.last_update_date = values[0]["datetime"]
                stock.save()
                updated = True
        if updated:
            channel_layer = get_channel_layer()
            for follower in stock.followers.all():
                async_to_sync(channel_layer.group_send)(
                    f"user_{follower.id}",
                    {
                        "type": "send.stock.update",  # This is the custom consumer type you define
                        "message": StockSerializer(stock).data,
                    },
                )


@shared_task
def periodic_update_time_series():
    symbols = Stock.objects.values_list("symbol", flat=True)
    for i, symbol in enumerate(symbols):
        batch_num = i // 8
        update_time_series.apply_async(kwargs={"symbol": symbol}, countdown=90 * batch_num)
