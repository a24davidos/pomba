# Makefile para o Arquetipo de Desenvolvemento

up:
	@echo "🚀 Levantando servizos de Docker..."
	docker compose --env-file "Docker/.env.development" -f "Docker/docker-compose.yml" up -d --wait
	@echo "🐍 Preparando contorna local de Python..."
	@chmod +x local_setup.sh
	@./local_setup.sh

down:
	@echo "🛑 Parando servizos..."
	docker compose -f "Docker/docker-compose.yml" down

build:
	@echo "🛠️ Reconstruíndo imaxes de Docker..."
	docker compose -f Docker/docker-compose.yml build --no-cache

clean:
	@echo "🧹 Limpeza profunda: borrando contedores e volumes..."
	docker compose -f Docker/docker-compose.yml down -v


up-prod:
	@echo "🚀 Levantando stack de producción..."
	docker compose --env-file "Docker/.env.prod" -f "Docker/docker-compose.prod.yml" up -d --wait

down-prod:
	@echo "🛑 Parando producción..."
	docker compose -f "Docker/docker-compose.prod.yml" down

build-prod:
	@echo "🛠️ Construíndo imaxes de producción..."
	docker compose -f Docker/docker-compose.prod.yml build --no-cache

clean-prod:
	@echo "🧹 Borrando contedores e volumes de producción..."
	docker compose -f Docker/docker-compose.prod.yml down -v


status:
	@docker exec garage /garage status

start-app:
	docker exec -it django_backend python manage.py startapp $(NAME)
