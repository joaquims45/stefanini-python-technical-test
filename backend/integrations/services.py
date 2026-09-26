import logging

from django.db import transaction
from django.utils import timezone

from .clients import get_all_clients
from .clients.base import SourceError
from .models import Item, SyncRun

logger = logging.getLogger("integrations.sync")


def _log_sync_run(sync_run: SyncRun) -> None:
    duration_ms = round(
        (sync_run.finished_at - sync_run.started_at).total_seconds() * 1000, 1
    )
    logger.info(
        "sync_source finalizado",
        extra={
            "source": sync_run.source,
            "success": sync_run.success,
            "records_count": sync_run.records_count,
            "duration_ms": duration_ms,
            "error_message": sync_run.error_message,
        },
    )


def sync_source(client) -> SyncRun:
    """Sincroniza uma única fonte.

    Em sucesso, faz upsert dos itens normalizados e registra um `SyncRun`
    bem-sucedido. Em falha, registra um `SyncRun` malsucedido com o motivo e
    **não mexe** nos itens já persistidos — dado antigo rotulado como antigo
    é mais útil que um painel vazio.
    """
    started_at = timezone.now()

    try:
        normalized_items = client.run()
    except SourceError as exc:
        sync_run = SyncRun.objects.create(
            source=client.source,
            started_at=started_at,
            finished_at=timezone.now(),
            success=False,
            records_count=0,
            error_message=str(exc),
        )
        _log_sync_run(sync_run)
        return sync_run

    with transaction.atomic():
        for data in normalized_items:
            Item.objects.update_or_create(
                source=data["source"],
                external_id=data["external_id"],
                defaults={
                    "title": data["title"],
                    "category": data.get("category"),
                    "event_date": data.get("event_date"),
                    "payload": data.get("payload", {}),
                },
            )

    sync_run = SyncRun.objects.create(
        source=client.source,
        started_at=started_at,
        finished_at=timezone.now(),
        success=True,
        records_count=len(normalized_items),
    )
    _log_sync_run(sync_run)
    return sync_run


def sync_all_sources() -> list[SyncRun]:
    """Sincroniza todas as fontes configuradas, cada uma isoladamente — a
    falha de uma não impede a sincronização das demais."""
    return [sync_source(client) for client in get_all_clients()]
