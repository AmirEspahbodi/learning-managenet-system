import os

os.system("poetry run python manage.py migrate --noinput")

# os.system(
#     "gunicorn django_core.asgi:application -w 4 --threads 8 -k django_core.uvicorn_worker.CustomWorker --bind 0.0.0.0:8082"
# )

os.system("poetry run python manage.py runserver 0.0.0.0:8082")
