web: gunicorn core.wsgi --log-file -
release: python manage.py migrate --noinput --verbosity 2 && python manage.py collectstatic --noinput && python manage.py init_data