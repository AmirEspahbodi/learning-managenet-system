#!/bin/bash

# remove existing image
sudo docker image rm lms_base_image:latest

# Build Docker image
sudo sudo docker build -t lms_base_image:latest -f ./docker/base.Dockerfile .

#sudo docker compose up --build -d
