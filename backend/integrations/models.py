from django.db import models


class Source(models.TextChoices):
    """Fontes externas suportadas pelo painel."""

    BRASILAPI_FERIADOS = "brasilapi_feriados", "BrasilAPI - Feriados Nacionais"
    OPEN_BREWERY_DB = "open_brewery_db", "Open Brewery DB"


class Item(models.Model):
    """Item normalizado, unificando o formato das duas fontes externas."""

    source = models.CharField(max_length=32, choices=Source.choices)
    external_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"], name="unique_item_per_source"
            )
        ]
        ordering = ["source", "title"]

    def __str__(self):
        return f"[{self.source}] {self.title}"


class SyncRun(models.Model):
    """Histórico de tentativas de sincronização de cada fonte."""

    source = models.CharField(max_length=32, choices=Source.choices)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    success = models.BooleanField()
    records_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-finished_at"]

    def __str__(self):
        status = "ok" if self.success else "falhou"
        return f"[{self.source}] {status} em {self.finished_at:%Y-%m-%d %H:%M:%S}"
