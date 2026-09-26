import pytest

from integrations.clients.base import SourceTimeoutError, SourceUnavailableError
from integrations.models import Item, Source, SyncRun
from integrations.services import sync_all_sources, sync_source


class FakeClient:
    """Cliente falso, mesma interface de BaseSourceClient, sem HTTP real."""

    def __init__(self, source, items=None, error=None):
        self.source = source
        self._items = items or []
        self._error = error

    def run(self):
        if self._error:
            raise self._error
        return self._items


def make_item(source, external_id, title, category="cat"):
    return {
        "source": source,
        "external_id": external_id,
        "title": title,
        "category": category,
        "event_date": None,
        "payload": {"raw": True},
    }


@pytest.mark.django_db
class TestSyncSource:
    def test_sucesso_persiste_itens_e_registra_sync_run_ok(self):
        client = FakeClient(
            Source.OPEN_BREWERY_DB,
            items=[make_item(Source.OPEN_BREWERY_DB, "1", "Cervejaria A")],
        )

        sync_run = sync_source(client)

        assert sync_run.success is True
        assert sync_run.records_count == 1
        assert sync_run.error_message is None
        assert Item.objects.count() == 1
        assert Item.objects.get().title == "Cervejaria A"

    def test_upsert_atualiza_item_existente_sem_duplicar(self):
        client_v1 = FakeClient(
            Source.OPEN_BREWERY_DB,
            items=[make_item(Source.OPEN_BREWERY_DB, "1", "Nome Antigo")],
        )
        client_v2 = FakeClient(
            Source.OPEN_BREWERY_DB,
            items=[make_item(Source.OPEN_BREWERY_DB, "1", "Nome Novo")],
        )

        sync_source(client_v1)
        sync_source(client_v2)

        assert Item.objects.count() == 1
        assert Item.objects.get().title == "Nome Novo"

    def test_falha_nao_persiste_item_e_registra_sync_run_com_erro(self):
        client = FakeClient(
            Source.BRASILAPI_FERIADOS, error=SourceTimeoutError("timeout simulado")
        )

        sync_run = sync_source(client)

        assert sync_run.success is False
        assert sync_run.records_count == 0
        assert "timeout simulado" in sync_run.error_message
        assert Item.objects.count() == 0

    def test_falha_nao_apaga_itens_de_sync_anterior_bem_sucedida(self):
        client_ok = FakeClient(
            Source.BRASILAPI_FERIADOS,
            items=[make_item(Source.BRASILAPI_FERIADOS, "2026-01-01", "Ano Novo")],
        )
        client_falho = FakeClient(
            Source.BRASILAPI_FERIADOS, error=SourceUnavailableError("fora do ar")
        )

        sync_source(client_ok)
        sync_source(client_falho)

        assert Item.objects.count() == 1
        assert SyncRun.objects.filter(success=False).count() == 1
        assert SyncRun.objects.filter(success=True).count() == 1


@pytest.mark.django_db
class TestSyncAllSources:
    def test_falha_de_uma_fonte_nao_impede_sincronizacao_da_outra(self, monkeypatch):
        clientes = [
            FakeClient(
                Source.BRASILAPI_FERIADOS,
                items=[make_item(Source.BRASILAPI_FERIADOS, "2026-01-01", "Ano Novo")],
            ),
            FakeClient(
                Source.OPEN_BREWERY_DB, error=SourceUnavailableError("fora do ar")
            ),
        ]
        monkeypatch.setattr(
            "integrations.services.get_all_clients", lambda: clientes
        )

        resultados = sync_all_sources()

        assert len(resultados) == 2
        assert {r.source: r.success for r in resultados} == {
            Source.BRASILAPI_FERIADOS: True,
            Source.OPEN_BREWERY_DB: False,
        }
        assert Item.objects.filter(source=Source.BRASILAPI_FERIADOS).count() == 1
        assert Item.objects.filter(source=Source.OPEN_BREWERY_DB).count() == 0
