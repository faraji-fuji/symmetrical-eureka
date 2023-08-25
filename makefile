migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

dev:
	python manage.py runserver


flush:
	python manage.py flush --noinput