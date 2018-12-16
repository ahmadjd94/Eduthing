# Eduthing

docker-compose up -d

docker ps 

docker exec -it postgres /bin/bash

psql -U postgres -p 
password = postgres

"
create database eduthing;

\q
"


virtualenv env -p python3

source env/bin/activate
pip3 install -r requirements.txt


./manage.py makemigrations

./manage.py migrate

./manage.py runserver