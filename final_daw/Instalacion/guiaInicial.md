## 1. Garage S3: Almacenamiento de Objetos
**¿Qué hemos hecho?** 
En lugar de guardar las fotos en una carpeta local que se borra al apagar el contenedor, usamos **Garage**. Es un servidor de almacenamiento compatible con el protocolo S3 de Amazon, pero que corre en tu propia infraestructura.

### Guía para replicarlo:
1.  **Levantar el servicio:** En el `docker-compose.yml`, definimos una imagen de Garage.
2.  **Configurar el Bucket:** Se debe entrar al contenedor de Garage y ejecutar comandos para:
    *   Crear una "Key" (Access Key y Secret Key).
    *   Crear un "Bucket" (el contenedor de archivos, ej: `mi-bucket-app`).
    *   Asociar la llave al bucket con permisos de lectura/escritura.
3.  **Variables clave:**
    *   `AWS_ACCESS_KEY_ID`: Tu usuario de Garage.
    *   `AWS_SECRET_ACCESS_KEY`: Tu contraseña de Garage.
    *   `AWS_S3_ENDPOINT_URL`: `http://garage:3900` (el nombre del servicio en Docker).

---

## 2. Configuración del Backend (PostgreSQL)
**¿Qué hemos hecho?** 
Cambiamos la base de datos por defecto (SQLite) por **PostgreSQL**, que es el estándar de la industria por su robustez.

### Guía para replicarlo:
1.  **Instalar el Driver:** Necesitas `psycopg2-binary` en tu `requirements.txt`.
2.  **Configurar `settings.py`:** En el diccionario `DATABASES`, cambiamos el `ENGINE` a `django.db.backends.postgresql`.
3.  **Conexión dinámica:** Usamos `os.getenv` para leer los datos del archivo `.env`:
    *   `NAME`: El nombre de la DB.
    *   `USER` y `PASSWORD`: Las credenciales que pusiste en el `.env`.
    *   `HOST`: `db` (el nombre del servicio en tu `docker-compose.yml`).

---

## 3. Integración Django + Garage (django-storages)
**¿Qué hemos hecho?** 
Hicimos que Django sea "consciente" de que no debe escribir en el disco duro, sino enviar todo a Garage por red.

### Guía para replicarlo:
1.  **Librería:** Instalamos `django-storages[s3]` y `boto3`.
2.  **Configuración en `settings.py`:**
    *   Añadir `'storages'` a `INSTALLED_APPS`.
    *   Configurar el diccionario `STORAGES` definiendo que el backend por defecto es `S3Storage`.
    *   **Truco del Proxy:** Usamos `AWS_S3_CUSTOM_DOMAIN = f"localhost:3900/{BUCKET}"` para que, cuando estés en tu Mac, el navegador sepa que las fotos se ven por el puerto 3900 y no intente buscarlas dentro de Django.

---

## 4. CORS: El puente con Vue 3
**¿Qué hemos hecho?** 
Por seguridad, los navegadores bloquean peticiones entre diferentes puertos (ej: de Vue en el 5173 a Django en el 8000). Hemos "abierto la frontera".

### Guía para replicarlo:
1.  **Librería:** `django-cors-headers`.
2.  **Middleware:** Es **crítico** que `'corsheaders.middleware.CorsMiddleware'` esté arriba del todo en la lista de `MIDDLEWARE` en `settings.py`.
3.  **Permisos:** Usamos `CORS_ALLOW_ALL_ORIGINS = True` para desarrollo, lo que permite que cualquier frontend (como tu Vue) le hable al backend sin que el navegador lo bloquee.

---

## 5. El "Hack" de la ruta de Python (PYTHONPATH)
**¿Qué hemos hecho?** 
Como tu estructura de Docker instala las librerías en una carpeta personalizada (`/app/libraries/lib/python3.12/site-packages`) en lugar de la carpeta estándar de Python, Django se volvía "ciego" y no encontraba sus propios archivos.

### Guía para replicarlo:
Hay dos formas de arreglarlo y hemos aplicado la más directa:
1.  **Modificar `manage.py`:** Añadimos `sys.path.append('/ruta/a/tus/librerias')` antes de que se ejecute nada.
2.  **¿Por qué?** Esto garantiza que cada vez que lances un comando como `migrate` o `runserver`, Python incluya esa carpeta en su mapa de búsqueda.

---

### Resumen del flujo de trabajo (Workflow)
Para replicar todo en un proyecto nuevo, el orden sería:
1.  Definir el **`.env`** con todas las llaves.
2.  Configurar el **`docker-compose.yml`** con los 4 servicios (db, backend, elastic, garage).
3.  Preparar el **`requirements.txt`** con las 4 patas (Django, Postgres, Storages, Cors).
4.  Ajustar **`settings.py`** para leer el `.env` y usar los backends de S3 y Postgres.
5.  Inyectar la ruta en **`manage.py`**.
6.  **Migrar y crear superusuario.**

¿Te gustaría que profundicemos en los comandos específicos de la consola para configurar el Bucket de Garage desde cero (la parte de las Keys)?
