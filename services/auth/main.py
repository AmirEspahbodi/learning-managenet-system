import os

os.system("poetry run python manage.py migrate --noinput")

os.system("poetry run python manage.py runserver 0.0.0.0:8082")
