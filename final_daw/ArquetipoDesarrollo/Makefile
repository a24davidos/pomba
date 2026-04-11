# Makefile para o Arquetipo de Desenvolvemento

up:
	@echo "🚀 Levantando servizos de Docker..."
	docker compose --env-file Docker/.env -f Docker/docker-compose.yml up -d --wait
	@echo "🐍 Preparando contorna local de Python..."
	@chmod +x local_setup.sh
	@./local_setup.sh
	@echo "🏗️ Configurando infraestrutura de Garage..."
	@chmod +x scripts/setup_infrastructure.sh
	@./scripts/setup_infrastructure.sh
	@echo "✨ Todo listo! Xa podes empezar a traballar."

down:
	@echo "🛑 Parando servizos..."
	docker compose -f Docker/docker-compose.yml down

# Limpeza total: detén contedores e borra volumes (base de datos e S3)
clean:
	@echo "🧹 Limpeza profunda: borrando contedores e volumes..."
	docker compose -f Docker/docker-compose.yml down -v

# Reconstruír imaxes dende cero
build:
	@echo "🛠️ Reconstruíndo imaxes de Docker..."
	docker compose -f Docker/docker-compose.yml build --no-cache

# Ver o estado do cluster de Garage
status:
	@docker exec garage /garage status