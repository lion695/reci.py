release: python manage.py migrate --noinput && (python manage.py createsuperuser --noinput || true)
web: gunicorn project.wsgi
