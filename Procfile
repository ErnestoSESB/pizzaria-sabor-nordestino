web: gunicorn core.wsgi --log-file -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python railway_init.py