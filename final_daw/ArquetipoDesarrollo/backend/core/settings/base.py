from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Aplicacións instaladas
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'users',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages',
    'django_elasticsearch_dsl',
    "drf_standardized_errors",
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
     "EXCEPTION_HANDLER": ('drf_standardized_errors.handler.exception_handler'),
}

# Para excepciones que no se manejan
DRF_STANDARDIZED_ERRORS = {"ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True}


SIMPLE_JWT = {
    # El token de acceso caducará en solo 1 dia
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    
    # El token de refresco durará 2 días
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    #Esto genera un nuevo refresh cada vez
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Orixes permitidos para desenvolvemento (Adaptado para Vue 3 / Vite)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        # Evita que la clave contenga el nombre o email del usuario
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        #Minimo de tamaño de la conraseña
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        # Evita claves comunes como "123456" o "password"
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Evita que la clave sea 100% numérica
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.User'
