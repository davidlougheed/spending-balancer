#!/usr/bin/env bash

# Docker run script

python manage.py makemigrations admin auth
python manage.py migrate --noinput
python manage.py collectstatic --noinput

uvicorn spending_balancer.asgi:application \
  --workers 1 \
  --loop uvloop \
  --host "0.0.0.0" \
  --port 8000
