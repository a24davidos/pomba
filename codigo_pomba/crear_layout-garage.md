docker compose up -d garage
docker exec -it garage /garage status
docker exec -it garage /garage node id
docker exec -it garage /garage layout assign -z dc1 -c 1G pones el node id que te da 
docker exec -it garage /garage layout apply --version 1
docker exec -it garage /garage bucket create mi-bucket-app
docker exec -it garage /garage key create django-app

Lo que te da lo copias a: 
AWS_ACCESS_KEY_ID=GK8e42000bf7a3543971930049
AWS_SECRET_ACCESS_KEY=...

docker exec -it garage /garage bucket allow --read --write mi-bucket-app --key django-app