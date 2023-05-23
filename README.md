# Installation
This project can be installed via virtualenv and python 3.11 or docker compose. For the sake of simplicity I'll describe docker installation.

`docker-compose up --build`

Run migrations

`docker-compose run --rm app python manage.py migrate`

