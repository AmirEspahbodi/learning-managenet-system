#!/bin/bash

sudo docker image rm python_lms_base_image:latest
sudo sudo docker build -t python_lms_base_image:latest -f ./backend/docker/base.Dockerfile .
