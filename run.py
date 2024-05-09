import os

os.system("sudo docker build -t lms_base_image:latest -f ./docker/base.Dockerfile .")
os.system("sudo docker compose up --build -d")
