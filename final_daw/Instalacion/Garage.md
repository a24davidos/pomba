------

## 1. Infraestructura y Almacenamiento S3 (Garage)

Garage es el corazón de tu gestión de archivos. A diferencia de un sistema de archivos tradicional, Garage trata cada archivo como un "objeto" accesible vía URL.

### A. Configuración Inicial (`garage.toml`)

Antes de arrancar el contenedor, definimos las reglas del juego en el archivo de configuración:

- **Puertos:** El **3900** es para la API S3 (donde Django envía fotos) y el **3901** para que los nodos hablen entre sí.
- **Persistencia:** Mapeamos `/var/lib/garage/data` y `/var/lib/garage/meta` a carpetas en tu Mac para que los datos no mueran al apagar Docker.

### B. Activación del Nodo y Capacidad

Este fue el paso crucial para que Garage "despertara":

1. **Obtener ID:** `docker exec garage garage node id`.
2. **Asignar Capacidad:** `docker exec garage garage layout assign [ID] -z dc1 -c 1G`.
   - Aquí le dimos una **identidad geográfica** (`dc1`) y un **límite de disco** (`1G`). Sin este comando, Garage está en modo "solo lectura" o inactivo.
3. **Aplicar el diseño:** `docker exec garage garage layout apply --version 1`. Esto escribe la configuración en el clúster.

### C. Seguridad y Acceso (Buckets y Keys)

Para que Django pueda entrar, creamos una "llave de casa":

1. **Crear Key:** `garage key create mi-llave`. Genera un Access Key y un Secret Key.
2. **Crear Bucket:** `garage bucket create mi-bucket-app`. Es el contenedor lógico.
3. **Autorización:** `garage bucket allow --read --write --key mi-llave mi-bucket-app`. Vinculamos la llave al cubo con permisos totales.

------

## 2. Configuración del Backend y Base de Datos

Aquí es donde Django deja de usar archivos locales y se convierte en una aplicación preparada para la nube.

### A. El Motor: PostgreSQL

Sustituimos SQLite por Postgres para tener una base de datos real y escalable.

- **Servicio Docker:** Se define un contenedor `db` con la imagen `postgres:15`.
- **Variables de Entorno:** Usamos el archivo `.env` para que Django sepa el usuario, contraseña y nombre de la base de datos sin escribirlo directamente en el código.

### B. El Puente: `django-storages`

Django no sabe hablar "S3" por defecto. Instalamos `django-storages` y `boto3`:

- **Configuración:** En `settings.py`, cambiamos el backend de almacenamiento.
- **Endpoint:** Le decimos a Django que su servidor S3 no es Amazon, sino `http://garage:3900`.
- **Truco del Localhost:** Configuramos `AWS_S3_CUSTOM_DOMAIN` para que las URLs que Django genera apunten a `localhost:3900`, permitiendo que tu navegador en el Mac vea las fotos.

------

## 3. Seguridad CORS y Rutas de Python

Estos son los ajustes "invisibles" que permiten que todo el sistema fluya sin errores de permisos o de archivos no encontrados.

### A. CORS (Cross-Origin Resource Sharing)

Vue corre en el puerto `5173` y Django en el `8000`. Por seguridad, el navegador bloquea que Vue le pida datos a Django.

- **Solución:** Instalamos `django-cors-headers`.
- **Ajuste:** Añadimos el middleware al principio de la lista y configuramos `CORS_ALLOW_ALL_ORIGINS = True`. Esto le dice a Django: "Acepta peticiones de cualquier sitio (incluyendo mi Vue)".

### B. El Hack del `PYTHONPATH`

Tu estructura de carpetas en Docker es especial: instalas las librerías en `/app/libraries`.

- **El Problema:** Al ejecutar comandos de Django desde la terminal del Mac (vía Docker), Python no busca en esa carpeta y dice "Django no está instalado".
- **La Solución:** Modificamos `manage.py` para añadir esa ruta manualmente con `sys.path.append()`. Esto garantiza que, no importa desde dónde lances el comando, Django encuentre sus herramientas.

------

He detallado estos tres bloques que forman la base de tu proyecto. **¿Te gustaría que continuemos ahora con la parte del Frontend en Vue 3 y cómo empezar a conectar la primera petición con este backend que ya tienes listo?**