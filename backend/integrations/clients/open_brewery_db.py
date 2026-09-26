from django.conf import settings

from integrations.models import Source

from .base import BaseSourceClient


class OpenBreweryDbClient(BaseSourceClient):
    """Cervejarias (Open Brewery DB). Resposta: lista de objetos
    `{"id": "...", "name": "...", "brewery_type": "...", ...}`."""

    source = Source.OPEN_BREWERY_DB

    def __init__(self, url=None):
        self.url = url or settings.OPEN_BREWERY_DB_URL

    def normalize(self, raw_data):
        if not isinstance(raw_data, list):
            raise TypeError("esperava uma lista de cervejarias")

        return [
            {
                "source": self.source,
                "external_id": entry["id"],
                "title": entry["name"],
                "category": entry.get("brewery_type"),
                "event_date": None,
                "payload": entry,
            }
            for entry in raw_data
        ]
