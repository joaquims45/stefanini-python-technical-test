from datetime import date

from django.conf import settings

from integrations.models import Source

from .base import BaseSourceClient


class BrasilApiFeriadosClient(BaseSourceClient):
    """Feriados nacionais (BrasilAPI). Resposta: lista de objetos
    `{"date": "2026-01-01", "name": "...", "type": "national"}`."""

    source = Source.BRASILAPI_FERIADOS

    def __init__(self, url=None):
        self.url = url or settings.BRASILAPI_FERIADOS_URL

    def normalize(self, raw_data):
        if not isinstance(raw_data, list):
            raise TypeError("esperava uma lista de feriados")

        return [
            {
                "source": self.source,
                "external_id": entry["date"],
                "title": entry["name"],
                "category": entry.get("type"),
                "event_date": date.fromisoformat(entry["date"]),
                "payload": entry,
            }
            for entry in raw_data
        ]
