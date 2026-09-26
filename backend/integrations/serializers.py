from rest_framework import serializers

from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "id",
            "source",
            "external_id",
            "title",
            "category",
            "event_date",
            "payload",
            "created_at",
            "updated_at",
        ]


class SourceHealthSerializer(serializers.Serializer):
    source = serializers.CharField()
    label = serializers.CharField()
    is_responding = serializers.BooleanField()
    last_successful_sync = serializers.DateTimeField(allow_null=True)
    records_count = serializers.IntegerField()
    last_error = serializers.CharField(allow_null=True)
    last_error_at = serializers.DateTimeField(allow_null=True)
