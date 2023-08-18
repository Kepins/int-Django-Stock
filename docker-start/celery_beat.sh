#!/bin/bash

celery -A djangostock beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
