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

lid:
	python manage.py loaddata init_data.json

init:
	python manage.py makemigrations && python manage.py migrate && python manage.py loaddata init_data.json