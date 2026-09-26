from django.core.management.base import BaseCommand
from django_q.models import Schedule

SCHEDULE_NAME = "sync_all_sources"
SYNC_FUNC = "integrations.services.sync_all_sources"


class Command(BaseCommand):
    """Cria ou atualiza o agendamento periódico de sincronização (django-q2).

    Idempotente por design (update_or_create pelo nome fixo do agendamento):
    pode ser chamado toda vez que o container sobe sem duplicar o Schedule.
    """

    help = "Cria ou atualiza o agendamento periódico de sincronização (django-q2)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
            default=5,
            help="Intervalo em minutos entre sincronizações (padrão: 5).",
        )

    def handle(self, *args, **options):
        minutes = options["minutes"]
        schedule, created = Schedule.objects.update_or_create(
            name=SCHEDULE_NAME,
            defaults={
                "func": SYNC_FUNC,
                "schedule_type": Schedule.MINUTES,
                "minutes": minutes,
                "repeats": -1,
            },
        )
        acao = "criado" if created else "atualizado"
        self.stdout.write(
            self.style.SUCCESS(
                f"Agendamento '{SCHEDULE_NAME}' {acao}: a cada {minutes} minuto(s)."
            )
        )
