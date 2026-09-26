from django.core.management.base import BaseCommand

from integrations.services import sync_all_sources


class Command(BaseCommand):
    help = "Executa uma sincronização única de todas as fontes externas."

    def handle(self, *args, **options):
        resultados = sync_all_sources()
        for sync_run in resultados:
            if sync_run.success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{sync_run.source}] OK - {sync_run.records_count} registro(s)"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"[{sync_run.source}] FALHOU - {sync_run.error_message}"
                    )
                )
