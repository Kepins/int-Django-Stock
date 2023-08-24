import os
import sys
from pathlib import Path

import django

sys.path.append(Path(__file__).parent.parent.parent.parent.as_posix())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangostock.settings.local")
django.setup()

from django_celery_beat.models import IntervalSchedule, PeriodicTask

schedule, created = IntervalSchedule.objects.get_or_create(
    every=12,
    period=IntervalSchedule.HOURS,
)

if not PeriodicTask.objects.filter(name="Updating StockTimeSeries").exists():
    PeriodicTask.objects.create(
        interval=schedule,  # we created this above.
        name="Updating StockTimeSeries",  # simply describes this periodic task.
        task="djangostock.application.tasks.periodic_update_time_series",  # name of task.
    )
