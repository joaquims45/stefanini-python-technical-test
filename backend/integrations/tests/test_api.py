import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from integrations.models import Item, Source, SyncRun


@pytest.fixture
def api_client():
    return APIClient()


def make_item(source, external_id, title):
    return Item.objects.create(
        source=source, external_id=external_id, title=title, payload={}
    )


def make_sync_run(source, success, records_count=0, error_message=None, when=None):
    when = when or timezone.now()
    return SyncRun.objects.create(
        source=source,
        started_at=when,
        finished_at=when,
        success=success,
        records_count=records_count,
        error_message=error_message,
    )


@pytest.mark.django_db
class TestItemsEndpoint:
    def test_lista_itens_das_duas_fontes(self, api_client):
        make_item(Source.BRASILAPI_FERIADOS, "2026-01-01", "Ano Novo")
        make_item(Source.OPEN_BREWERY_DB, "1", "Cervejaria A")

        response = api_client.get("/items")

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_filtra_itens_por_fonte(self, api_client):
        make_item(Source.BRASILAPI_FERIADOS, "2026-01-01", "Ano Novo")
        make_item(Source.OPEN_BREWERY_DB, "1", "Cervejaria A")

        response = api_client.get("/items", {"source": Source.OPEN_BREWERY_DB})

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["source"] == Source.OPEN_BREWERY_DB


@pytest.mark.django_db
class TestHealthEndpoint:
    def test_fonte_nunca_sincronizada_aparece_como_nao_respondendo(self, api_client):
        response = api_client.get("/health")

        assert response.status_code == 200
        assert len(response.data) == len(Source.values)
        for entry in response.data:
            assert entry["is_responding"] is False
            assert entry["last_successful_sync"] is None
            assert entry["records_count"] == 0
            assert entry["last_error"] is None

    def test_reflete_ultima_sync_bem_sucedida_e_contagem_de_itens(self, api_client):
        make_item(Source.OPEN_BREWERY_DB, "1", "Cervejaria A")
        make_sync_run(Source.OPEN_BREWERY_DB, success=True, records_count=1)

        response = api_client.get("/health")

        entry = next(
            e for e in response.data if e["source"] == Source.OPEN_BREWERY_DB
        )
        assert entry["is_responding"] is True
        assert entry["last_successful_sync"] is not None
        assert entry["records_count"] == 1
        assert entry["last_error"] is None

    def test_falha_mais_recente_marca_nao_respondendo_mas_preserva_ultimo_sucesso(
        self, api_client
    ):
        antes = timezone.now() - timezone.timedelta(hours=1)
        agora = timezone.now()
        make_sync_run(
            Source.BRASILAPI_FERIADOS, success=True, records_count=5, when=antes
        )
        make_sync_run(
            Source.BRASILAPI_FERIADOS,
            success=False,
            error_message="serviço fora do ar",
            when=agora,
        )

        response = api_client.get("/health")

        entry = next(
            e for e in response.data if e["source"] == Source.BRASILAPI_FERIADOS
        )
        assert entry["is_responding"] is False
        assert entry["last_successful_sync"] is not None
        assert entry["last_error"] == "serviço fora do ar"
