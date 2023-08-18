#!/bin/bash

celery -A djangostock worker --loglevel=INFO
