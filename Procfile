web: gunicorn core.wsgi --log-file -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py init_data