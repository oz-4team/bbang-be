#!/bin/sh
set -e
python manage.py makemigrations --noinput  # 변경 사항 적용
python manage.py migrate --noinput  # 마이그레이션 실행
gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2