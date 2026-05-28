from .base import *

# En producción nunca DEBUG=True: Django mostraría stack traces completos
DEBUG = False

# Django solo responde a peticiones dirigidas a estos dominios.
ALLOWED_HOSTS = ['pomba.app', 'www.pomba.app']

# Orígenes permitidos para hacer peticiones AJAX/fetch desde el navegador.
CORS_ALLOWED_ORIGINS = [
    'https://pomba.app',
]

# Django rechaza cualquier POST/PUT/DELETE cuyo header Origin no esté aquí.
CSRF_TRUSTED_ORIGINS = [
    'https://pomba.app',
    'https://www.pomba.app',
]

# Redirigimos automáticamente cualquier petición HTTP a HTTPS.
SECURE_SSL_REDIRECT = True

# Le dice a Django que confíe en la cabecera X-Forwarded-Proto que pone Nginx.
# Necesario porque Nginx termina el SSL y habla con Django por HTTP interno.
# Sin esto SECURE_SSL_REDIRECT entraría en bucle infinito.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# La cookie de sesión solo se envía por HTTPS, nunca por HTTP en claro.
SESSION_COOKIE_SECURE = True

# El token CSRF solo se envía por HTTPS.
CSRF_COOKIE_SECURE = True

# En producción solo loguear WARNING o superior así me evito ruido innecesario.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
