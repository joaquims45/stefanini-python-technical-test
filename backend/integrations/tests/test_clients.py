import pytest
import responses
from requests.exceptions import Timeout

from integrations.clients.base import (
    SourceFormatError,
    SourceTimeoutError,
    SourceUnavailableError,
)
from integrations.clients.brasilapi_feriados import BrasilApiFeriadosClient
from integrations.clients.open_brewery_db import OpenBreweryDbClient
from integrations.models import Source

FERIADOS_URL = "https://example.test/feriados"
BREWERIES_URL = "https://example.test/breweries"

CLIENTS = [
    (BrasilApiFeriadosClient, FERIADOS_URL),
    (OpenBreweryDbClient, BREWERIES_URL),
]


@pytest.mark.parametrize("client_cls,url", CLIENTS)
class TestSourceClientsResilience:
    """Os três cenários obrigatórios: timeout, 500 e formato inesperado."""

    @responses.activate
    def test_timeout_vira_source_timeout_error(self, client_cls, url):
        responses.add(responses.GET, url, body=Timeout())
        client = client_cls(url=url)

        with pytest.raises(SourceTimeoutError):
            client.run()

    @responses.activate
    def test_erro_500_vira_source_unavailable_error(self, client_cls, url):
        responses.add(responses.GET, url, status=500)
        client = client_cls(url=url)

        with pytest.raises(SourceUnavailableError):
            client.run()

    @responses.activate
    def test_json_invalido_vira_source_format_error(self, client_cls, url):
        responses.add(
            responses.GET, url, body="isso não é JSON", content_type="text/plain"
        )
        client = client_cls(url=url)

        with pytest.raises(SourceFormatError):
            client.run()

    @responses.activate
    def test_schema_inesperado_vira_source_format_error(self, client_cls, url):
        responses.add(responses.GET, url, json={"nao": "e uma lista"})
        client = client_cls(url=url)

        with pytest.raises(SourceFormatError):
            client.run()


class TestBrasilApiFeriadosNormalize:
    @responses.activate
    def test_normaliza_feriados_corretamente(self):
        responses.add(
            responses.GET,
            FERIADOS_URL,
            json=[{"date": "2026-01-01", "name": "Confraternização", "type": "national"}],
        )
        client = BrasilApiFeriadosClient(url=FERIADOS_URL)

        items = client.run()

        assert len(items) == 1
        item = items[0]
        assert item["source"] == Source.BRASILAPI_FERIADOS
        assert item["external_id"] == "2026-01-01"
        assert item["title"] == "Confraternização"
        assert item["category"] == "national"
        assert item["event_date"].isoformat() == "2026-01-01"


class TestOpenBreweryDbNormalize:
    @responses.activate
    def test_normaliza_cervejarias_corretamente(self):
        responses.add(
            responses.GET,
            BREWERIES_URL,
            json=[{"id": "abc-123", "name": "Cervejaria Teste", "brewery_type": "micro"}],
        )
        client = OpenBreweryDbClient(url=BREWERIES_URL)

        items = client.run()

        assert len(items) == 1
        item = items[0]
        assert item["source"] == Source.OPEN_BREWERY_DB
        assert item["external_id"] == "abc-123"
        assert item["title"] == "Cervejaria Teste"
        assert item["category"] == "micro"
        assert item["event_date"] is None
