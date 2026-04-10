up:
	docker compose -f Docker/docker-compose.yml up -d --wait
	@chmod +x local_setup.sh
	@./local_setup.sh

down:
	docker compose -f Docker/docker-compose.yml down

build:
	docker compose -f Docker/docker-compose.yml build --no-cache