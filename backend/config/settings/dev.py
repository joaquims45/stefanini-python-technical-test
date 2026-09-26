"""Settings de desenvolvimento/execução (Postgres via docker-compose)."""
import os

from .base import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "painel_integracoes"),
        "USER": os.environ.get("POSTGRES_USER", "painel"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "painel"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
