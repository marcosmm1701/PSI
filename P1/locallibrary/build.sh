pip3 install -r requirements.txt
python manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runscript populate_catalog
python3 manage.py createsuperuser