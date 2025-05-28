tw start:
	cd theme/static_src && npx @tailwindcss/cli -i ./src/style.css -o ../static/css/dist/style.css --watch && cd ../../

run:
	python manage.py runserver
