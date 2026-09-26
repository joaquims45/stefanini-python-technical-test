from django.db import transaction
from django.utils import timezone

from .clients import get_all_clients
from .clients.base import SourceError
from .models import Item, SyncRun


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
        return SyncRun.objects.create(
            source=client.source,
            started_at=started_at,
            finished_at=timezone.now(),
            success=False,
            records_count=0,
            error_message=str(exc),
        )

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

    return SyncRun.objects.create(
        source=client.source,
        started_at=started_at,
        finished_at=timezone.now(),
        success=True,
        records_count=len(normalized_items),
    )


def sync_all_sources() -> list[SyncRun]:
    """Sincroniza todas as fontes configuradas, cada uma isoladamente — a
    falha de uma não impede a sincronização das demais."""
    return [sync_source(client) for client in get_all_clients()]
