#!/bin/bash
pip3 install -r requirements.txt

python3 manage.py makemigrations
python3 manage.py migrate

python3 populate_catalog.py

python manage.py collectstatic --noinput

python3 manage.py createsuperuser

