from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Afecta a todas las peticiones (GET, POST, etc...)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# Solo afecta a peticiones que modifican estado (PUT, DELETE, PATCH, POST)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
]
