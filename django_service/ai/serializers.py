from rest_framework import serializers


class SummarizeSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(required=False)
    text = serializers.CharField(required=False, allow_blank=False)


class PrioritizeSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class ParseSerializer(serializers.Serializer):
    text = serializers.CharField()


class SimilarSerializer(serializers.Serializer):
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)
