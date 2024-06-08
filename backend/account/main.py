import os

# os.system("poetry run python manage.py migrate --noinput")

# os.system(
#     "gunicorn django_core.asgi:application -w 4 --threads 8 -k django_core.uvicorn_worker.CustomWorker --bind 0.0.0.0:8081"
# )

os.system("poetry run python account/manage.py runserver 0.0.0.0:8081")
