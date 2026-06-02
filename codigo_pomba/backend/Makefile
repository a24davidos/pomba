# Variables
CONTAINER=django_backend

# Entra no contedor da aplicación
bash:
	docker exec -it $(CONTAINER) bash

# Executar migracións.
migrate:
	docker exec -it $(CONTAINER) python manage.py makemigrations
	docker exec -it $(CONTAINER) python manage.py migrate

# Instalar unha libraría específica. (make install-lib LIB=django)
install-lib:
	docker exec -it $(CONTAINER) pip install $(LIB)
	docker exec -it $(CONTAINER) pip freeze > backend/requirements.txt

# Ver os logs dun contedor en específico.
logs:
	docker logs -f $(CONTAINER)

# App related

# Crea un superusuario para o admin de Django
createsuperuser:
	docker exec -it $(CONTAINER) python3 manage.py createsuperuser

# Crea unha aplicación Django. (make startapp APP=nome_app)
startapp:
	docker exec -it $(CONTAINER) python manage.py startapp $(APP)
	@echo "⚠️  Lembra engadir '$(APP)' a LOCAL_APPS no settings/base.py"