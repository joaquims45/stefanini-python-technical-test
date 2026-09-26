from .base import SourceError, SourceFormatError, SourceTimeoutError, SourceUnavailableError
from .brasilapi_feriados import BrasilApiFeriadosClient
from .open_brewery_db import OpenBreweryDbClient

__all__ = [
    "SourceError",
    "SourceFormatError",
    "SourceTimeoutError",
    "SourceUnavailableError",
    "BrasilApiFeriadosClient",
    "OpenBreweryDbClient",
    "get_all_clients",
]


def get_all_clients():
    """Lista os clientes de todas as fontes suportadas pelo painel."""
    return [BrasilApiFeriadosClient(), OpenBreweryDbClient()]
