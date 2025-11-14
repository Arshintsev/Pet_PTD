
from rest_framework import serializers


class ProfileStatsSerializer(serializers.Serializer):
    questions_learned = serializers.IntegerField()
    topics_learned = serializers.IntegerField()
    progress = serializers.CharField()
