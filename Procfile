web: gunicorn ediv_portal.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 180
release: python manage.py migrate --noinput
