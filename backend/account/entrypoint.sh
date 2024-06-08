#!/bin/sh

FILE=".pg_service.conf"
if [ -f "$FILE" ]; then
    # Using awk to extract variables
  HOST=$(awk -F= '/^host=/{print $2}' "$FILE")
  USER=$(awk -F= '/^user=/{print $2}' "$FILE")
  DBNAME=$(awk -F= '/^dbname=/{print $2}' "$FILE")
  PORT=$(awk -F= '/^port=/{print $2}' "$FILE")
  PASSWORD=$(awk -F= '/^password=/{print $2}' "$FILE")

  # Output the variables
  echo "Host: $HOST"
  echo "User: $USER"
  echo "DB Name: $DBNAME"
  echo "Port: $PORT"
  echo "Password: $PASSWORD"
else
  echo "Error: .pg_service.conf file not found!"
  exit 1
fi

echo "Waiting for postgres..."

while ! nc -z $HOST $PORT; do
  sleep 0.1
done

echo "PostgreSQL started"
#
#python manage.py flush --no-input
#python manage.py migrate

exec "$@"