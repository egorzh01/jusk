tw start:
	cd theme/static_src && npx @tailwindcss/cli -i ./src/style.css -o ../static/css/dist/style.css --watch && cd ../../

run:
	python manage.py runserver

mig:
	python manage.py migrate

makemig:
	python manage.py makemigrations

addsu:
	python manage.py createsuperuser --email "admin@admin.com"


pc:
	pre-commit run --all
