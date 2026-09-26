import pytest
from django.core.management import call_command
from django_q.models import Schedule

from integrations.management.commands.schedule_sync import SCHEDULE_NAME
from integrations.models import Item, Source, SyncRun


@pytest.mark.django_db
class TestScheduleSyncCommand:
    def test_cria_o_agendamento_na_primeira_chamada(self):
        call_command("schedule_sync", "--minutes", "10")

        assert Schedule.objects.filter(name=SCHEDULE_NAME).count() == 1
        schedule = Schedule.objects.get(name=SCHEDULE_NAME)
        assert schedule.minutes == 10
        assert schedule.func == "integrations.services.sync_all_sources"

    def test_e_idempotente_nao_duplica_ao_chamar_de_novo(self):
        call_command("schedule_sync", "--minutes", "5")
        call_command("schedule_sync", "--minutes", "15")

        assert Schedule.objects.filter(name=SCHEDULE_NAME).count() == 1
        assert Schedule.objects.get(name=SCHEDULE_NAME).minutes == 15


@pytest.mark.django_db
class TestSyncSourcesCommand:
    def test_roda_sync_all_sources_e_registra_historico(self, monkeypatch):
        def fake_sync_all_sources():
            return [
                SyncRun.objects.create(
                    source=Source.BRASILAPI_FERIADOS,
                    started_at="2026-01-01T00:00:00Z",
                    finished_at="2026-01-01T00:00:01Z",
                    success=True,
                    records_count=3,
                )
            ]

        monkeypatch.setattr(
            "integrations.management.commands.sync_sources.sync_all_sources",
            fake_sync_all_sources,
        )

        call_command("sync_sources")

        assert SyncRun.objects.count() == 1
        assert Item.objects.count() == 0
