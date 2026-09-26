from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Item, Source, SyncRun
from .serializers import ItemSerializer, SourceHealthSerializer


class ItemListView(ListAPIView):
    """GET /items?source=<fonte> — lista unificada das duas fontes."""

    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = Item.objects.all()
        source = self.request.query_params.get("source")
        if source:
            queryset = queryset.filter(source=source)
        return queryset


class HealthView(APIView):
    """GET /health — estado de cada integração."""

    def get(self, request):
        data = [self._source_health(source) for source in Source.values]
        serializer = SourceHealthSerializer(data, many=True)
        return Response(serializer.data)

    @staticmethod
    def _source_health(source):
        last_run = SyncRun.objects.filter(source=source).order_by("-finished_at").first()
        last_success = (
            SyncRun.objects.filter(source=source, success=True)
            .order_by("-finished_at")
            .first()
        )
        last_failure = (
            SyncRun.objects.filter(source=source, success=False)
            .order_by("-finished_at")
            .first()
        )

        return {
            "source": source,
            "label": Source(source).label,
            # "Está respondendo agora" reflete a última tentativa de sync, não
            # um ping ao vivo — ver decisão registrada no README.
            "is_responding": bool(last_run and last_run.success),
            "last_successful_sync": last_success.finished_at if last_success else None,
            "records_count": Item.objects.filter(source=source).count(),
            "last_error": last_failure.error_message if last_failure else None,
            "last_error_at": last_failure.finished_at if last_failure else None,
        }
