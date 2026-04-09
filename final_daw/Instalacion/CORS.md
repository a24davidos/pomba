## El mecanismo de intercambio de recursos de origen cruzado (CORS)

CORS no es una tecnología ligada a un framework específico como Vue o Django, sino una política de seguridad implementada directamente en los navegadores web. Su función principal es actuar como un guardián que restringe cómo una aplicación web cargada en un dominio puede interactuar con recursos de un origen distinto.

### Funcionamiento lógico

Cuando realizas una petición desde un origen (por ejemplo, `http://localhost:5173`) hacia otro servidor (como `http://localhost:8000`), el navegador intercepta la comunicación. Antes de permitir que el código JavaScript acceda a la respuesta, el navegador verifica si el servidor de destino incluye encabezados HTTP específicos que autoricen el origen de la solicitud.

Si el servidor responde con el encabezado `Access-Control-Allow-Origin: http://localhost:5173`, el navegador entrega los datos a la aplicación. De lo contrario, bloquea la respuesta por seguridad, incluso si el servidor procesó la solicitud correctamente.

### Seguridad y propósito

Esta restricción existe para prevenir ataques de **Cross-Site Request Forgery (CSRF)**. Sin CORS, un sitio web malicioso podría ejecutar peticiones en segundo plano hacia servicios donde el usuario tiene sesiones activas (como bancos o redes sociales) y extraer información privada aprovechando las cookies almacenadas en el navegador.

------

## Configuración en entorno de desarrollo y producción

Existen dos estrategias principales para gestionar la comunicación entre Django y Vue: configurar CORS en el servidor o utilizar un Proxy en el cliente.

### Opción A: Configuración en Django (Lado Servidor)

Esta es la solución estándar cuando el Frontend y el Backend residen en dominios o subdominios diferentes.

1. **Instalación:** Se debe instalar la librería `django-cors-headers`.

   Bash

   ```
   pip install django-cors-headers
   ```

2. **Configuración en settings.py:**

   - Añadir `corsheaders` a `INSTALLED_APPS`.
   - Añadir `corsheaders.middleware.CorsMiddleware` en la parte superior de `MIDDLEWARE`.
   - Definir los orígenes permitidos:

   Python

   ```
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:5173",
       "https://tu-dominio-produccion.com",
   ]
   ```

### Opción B: Configuración de Proxy en Vue (Lado Cliente)

Durante el desarrollo, para evitar tocar la configuración de Django, puedes configurar Vue para que "engañe" al navegador, haciendo que todas las peticiones parezcan venir del mismo origen.

1. **Archivo vite.config.js:**

   JavaScript

   ```
   export default defineConfig({
     server: {
       proxy: {
         '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true,
           secure: false,
         }
       }
     }
   })
   ```

2. **Resultado:** Al llamar a `/api/productos` desde Vue, el servidor de desarrollo de Vite redirige la petición a Django internamente, eliminando la necesidad de CORS en local.

------

## Implementación en el despliegue (Build de producción)

Cuando pasas a producción, la estrategia cambia dependiendo de la arquitectura de red.

### Escenario 1: Dominio Único (Recomendado)

Si sirves los archivos estáticos de Vue directamente desde Django o mediante un servidor como Nginx que unifica ambos bajo el mismo dominio (ej. `web.com` y `web.com/api`), **CORS no es necesario**.

**Pasos:**

1. Ejecutas `npm run build` en Vue.
2. Mueves los archivos de la carpeta `dist` a la carpeta de estáticos de Django o a la ruta que gestione Nginx.
3. El navegador detecta el mismo origen y permite la comunicación directa.

### Escenario 2: Dominios Separados

Si el Frontend está en un servicio (ej. Vercel) y el API en otro (ej. AWS/DigitalOcean), debes mantener la configuración de CORS en Django.

**Pasos:**

1. Configura `CORS_ALLOWED_ORIGINS` en Django con la URL final de tu aplicación Vue.
2. Asegúrate de que el servidor (Nginx/Gunicorn) permita el paso de los encabezados `Access-Control`.
3. En Vue, utiliza variables de entorno (`.env.production`) para que las peticiones apunten a la URL absoluta del servidor de Django.