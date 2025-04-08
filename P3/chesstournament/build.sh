#!/bin/bash
pip3 install -r requirements.txt

python3 manage.py makemigrations
python3 manage.py migrate

python manage.py collectstatic --noinput

python3 manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="alumnodb").exists():
    User.objects.create_superuser("alumnodb", "alumnodb@example.com", "alumnodb")
    print("Superusuario creado exitosamente.")
else:
    print("El superusuario ya existe.")
EOF