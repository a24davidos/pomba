# Pomba

**Pomba** é unha plataforma web de almacenamento persoal de ficheiros, deseñada como alternativa libre e privada a servizos como Google Drive ou Dropbox. Permite aos usuarios gardar, organizar e xestionar os seus documentos, imaxes e arquivos de audio dende o navegador, sen depender de terceiros que poidan facer uso dos seus datos.

O sistema ofrece autenticación segura con JWT, xestión de ficheiros en cartafoles, previsualización de contido (PDF, imaxes e audio) e un motor de busca baseado en Elasticsearch que permite localizar arquivos por nome, tipo ou metadatos. O almacenamento realízase mediante **Garage**, un sistema compatible co protocolo S3.

Unha das funcionalidades máis destacadas é o **control de versións de ficheiros de audio**, orientado a músicos que permite comparar e recuperar versións previas de calquera canción ou proxecto musical.

A aplicación está completamente contenerizada con Docker e segue unha arquitectura desacoplada: backend en **Django REST Framework**, frontend en **Vue.js 3**, base de datos **PostgreSQL**, motor de busca **Elasticsearch** e almacenamento de obxectos con **Garage**.

---

## Instalación / Posta en marcha

### Requisitos previos


- Docker e Docker Compose
- `make`
- Python 3.12+

### Pasos

**1. Clonar o repositorio**

```bash
git clone https://gitlab.iessanclemente.net/dawd/a24davidos.git
cd a24davidos/codigo_pomba
```

**2. Configurar as variables de entorno**

Copia o ficheiro de exemplo e completa os valores:

```bash
cp Docker/.env.development.example Docker/.env.development
```

Os campos obrigatorios son:

| Variable | Descripción |
|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django |
| `POSTGRES_DB` | Nome da base de datos |
| `POSTGRES_USER` | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | Contrasinal de PostgreSQL |
| `AWS_ACCESS_KEY_ID` | Clave de acceso do bucket Garage |
| `AWS_SECRET_ACCESS_KEY` | Clave secreta do bucket Garage |
| `GARAGE_RPC_SECRET` | Segredo RPC de Garage (cadea hexadecimal de 64 chars) |

Para xerar `GARAGE_RPC_SECRET` podes usar:
```bash
openssl rand -hex 32
```

**3. Configurar Garage (almacenamento S3)**

Consulta a sección [Tutorial: Crear un bucket en Garage](#tutorial-crear-un-bucket-en-garage) máis abaixo.

**4. Levantar os servizos**

```bash
make up
```

Isto levanta todos os contedores (Nginx, Django, Vue, PostgreSQL, Garage, Elasticsearch, Kibana) e instala as dependencias Python no entorno local.

**5. Crear un superusuario (opcional, para o admin de Django)**

```bash
docker exec -it django_backend python manage.py createsuperuser
```


---

## Tutorial: Crear un bucket en Garage

[Garage](https://garagehq.deuxfleurs.fr/) é un sistema de almacenamento de obxectos compatible con S3, lixeiro e ideal para autoaloxamento. A continuación explícase como inicializalo e crear o bucket que usa Pomba.

### 0. Configurar garage.toml

Antes de levantar Garage, é necesario ter o ficheiro `garage.toml` en `Docker/`. Hai un exemplo en `Docker/garage.toml.example`:

```bash
cp Docker/garage.toml.example Docker/garage.toml
```

O ficheiro configura os directorios de datos, os portos e o segredo RPC. Os valores por defecto funcionan para o stack de Docker, pero hai que asegurarse de que `rpc_secret` coincide co valor de `GARAGE_RPC_SECRET` no `.env`:

```toml
metadata_dir = "/var/lib/garage/meta"
data_dir     = "/var/lib/garage/data"
replication_factor = 1

rpc_bind_addr   = "0.0.0.0:3901"
rpc_public_addr = "garage:3901"
rpc_secret      = "pon-aqui-o-mesmo-valor-que-GARAGE_RPC_SECRET"

[s3_api]
s3_region    = "garage"
api_bind_addr = "0.0.0.0:3900"

[admin]
api_bind_addr = "0.0.0.0:3903"
```

### 1. Levantar só Garage

```bash
docker compose --env-file Docker/.env.development -f Docker/docker-compose.yml up -d garage
```

### 2. Ver o estado do clúster

```bash
docker exec -it garage /garage status
```

### 3. Obter o ID do nodo

```bash
docker exec -it garage /garage node id
```

Verás algo parecido a:

```
Garage node ID: a1b2c3d4e5f6...  (64 caracteres hexadecimais)
```

Copia os primeiros 16 caracteres do ID (ou o ID completo).

### 4. Asignar o layout ao nodo

```bash
docker exec -it garage /garage layout assign -z dc1 -c 1G <NODE_ID>
```

- `-z dc1` → zona do datacenter (pode ser calquera nome)
- `-c 1G` → capacidade asignada ao nodo
- `<NODE_ID>` → substitúe polo ID obtido no paso anterior

### 5. Aplicar o layout

```bash
docker exec -it garage /garage layout apply --version 1
```

### 6. Crear o bucket

```bash
docker exec -it garage /garage bucket create pomba-app
```

### 7. Crear unha clave de acceso

```bash
docker exec -it garage /garage key create django-app
```

A saída mostrará os valores de `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`. Cópiaos no teu `.env.development`:

```env
AWS_ACCESS_KEY_ID=GKxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 8. Dar permisos á clave sobre o bucket

```bash
docker exec -it garage /garage bucket allow --read --write pomba-app --key django-app
```

### 9. Verificar

```bash
docker exec -it garage /garage bucket list
docker exec -it garage /garage key list
```

Agora xa podes levantar o resto dos servizos con `make up`.

---

## Uso

A aplicación está accesible en:

| Servizo | URL |
|---|---|
| Aplicación web | [pomba.me](https://pomba.me) |
| API Swagger | [pomba.me/api/schema/swagger/](https://pomba.me/api/schema/swagger/) |

En local (modo desenvolvemento):

| Servizo | URL |
|---|---|
| Aplicación web | `http://localhost` |
| API Swagger | `http://localhost/api/schema/swagger/` |
| Admin Django | `http://localhost/admin/` |
| Kibana (Elasticsearch) | `http://localhost:5601` |

### Comandos útiles

**Desenvolvemento**

```bash
make up          # Levanta todos os servizos
make down        # Para todos os servizos
make build       # Reconstrúe as imaxes de Docker
make clean       # Elimina contedores e volumes (borra os datos)
```

**Producción**

```bash
make up-prod     # Levanta o stack de producción
make down-prod   # Para o stack de producción
make build-prod  # Constrúe as imaxes de producción
make clean-prod  # Elimina contedores e volumes de producción
```

**Outros**

```bash
make status      # Mostra o estado do clúster Garage
make start-app NAME=<nome>  # Crea unha nova app de Django
```

---

## Sobre a persoa autora

Son David Otero, estudante de Desenvolvemento de Aplicacións Web no IES San Clemente (Santiago de Compostela). Teño especial interese no desenvolvemento backend, a privacidade dixital e o software libre.

Elixín este proxecto porque quería construír algo con utilidade real: unha alternativa a Google Drive que calquera persoa poida autoaloxa no seu propio servidor, sen ceder os seus datos a terceiros nin depender de plataformas privativas. A crecente preocupación pola privacidade e o uso que grandes empresas fan dos datos dos usuarios foi o principal motivo para desenvolver Pomba.

Podes contactar comigo en: **a24davidos@iessanclemente.net**

---

## Licencia

Este proxecto está licenciado baixo a [GNU General Public License v3.0](LICENSE).

Podes usar, modificar e distribuír este software libremente, sempre que as versións derivadas manteñan a mesma licenza e o código fonte permaneza accesible. Consulta o ficheiro [LICENSE](LICENSE) para máis detalles.

---


## Guía de contribución

As contribucións son benvidas. Se queres colaborar:

1. Fai un *fork* do repositorio.
2. Crea unha rama nova para a túa funcionalidade: `git checkout -b feature/nova-funcionalidade`.
3. Fai os teus cambios e subeos con mensaxes descritivas.
4. Abre un *merge request* describindo o que fixeches e por que.

Algunhas áreas onde se pode contribuír:

- Novas funcionalidades (compartir ficheiros entre usuarios, editor Markdown...)
- Melloras de rendemento ou seguridade
- Tests automatizados
- Traducións da interface

---

## Memoria

1. [Estudo preliminar](doc/templates/1_estudo_preliminar.md)
2. [Análise](doc/templates/2_analise.md)
3. [Deseño](doc/templates/3_deseno.md)
4. [Planificación e Orzamento](doc/templates/a3_orzamento.md)
5. [Codificación e Probas](doc/templates/4_codificacion_probas.md)
6. [Futuro e comercialización](doc/templates/5_manuais.md)
