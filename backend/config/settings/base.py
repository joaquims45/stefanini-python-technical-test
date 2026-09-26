"""Settings compartilhados entre os ambientes (dev/test)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-nao-use-em-producao")

DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_q",
    "integrations",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# Sem autenticação de usuários no escopo do teste (ver README) — libera CORS
# para o Flutter Web consumir a API sem fricção.
CORS_ALLOW_ALL_ORIGINS = True

# Broker ORM do django-q2: usa o próprio Postgres para a fila, evitando
# depender de Redis só para rodar um cron simples (decisão registrada no
# README).
Q_CLUSTER = {
    "name": "painel_integracoes",
    "workers": 1,
    "timeout": 60,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}

# Fontes externas configuradas nos clientes (ver integrations/clients/).
BRASILAPI_FERIADOS_URL = os.environ.get(
    "BRASILAPI_FERIADOS_URL", "https://brasilapi.com.br/api/feriados/v1/2026"
)
OPEN_BREWERY_DB_URL = os.environ.get(
    "OPEN_BREWERY_DB_URL",
    "https://api.openbrewerydb.org/v1/breweries?per_page=20&page=1",
)
EXTERNAL_SOURCE_TIMEOUT = (3, 8)  # (connect, read) em segundos
