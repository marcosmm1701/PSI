#!/bin/bash
pip3 install -r requirements.txt

python3 manage.py makemigrations
python3 manage.py migrate

python3 populate_catalog.py

python manage.py collectstatic --noinput

python3 manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "tucontraseña123")
    print("Superusuario creado exitosamente.")
else:
    print("El superusuario ya existe.")
EOF

