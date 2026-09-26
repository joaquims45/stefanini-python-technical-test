"""Settings de teste: SQLite em memória, sem broker externo.

Os testes precisam rodar sem acesso à internet e sem depender de um banco de
dados externo em execução — por isso trocamos o Postgres por SQLite em
memória aqui, em vez de usar o mesmo banco do ambiente de dev. É a alternativa
mais simples que continua exercitando o ORM real (ao contrário de mockar o
banco inteiro).
"""
from .base import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# django-q2 roda as tasks de forma síncrona (sem broker/cluster real) durante
# os testes.
Q_CLUSTER = {
    **Q_CLUSTER,  # noqa: F405
    "sync": True,
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
