from django.contrib.admin.models import LogEntry
from rest_framework import serializers


ACTION_DATETIME_FORMAT = "%d %B %Y -- %H:%M:%S"


class AdminHistorySerializer(serializers.ModelSerializer):
    action_time = serializers.DateTimeField(format=ACTION_DATETIME_FORMAT)
    user = serializers.StringRelatedField()
    action = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = ["action_time", "user", "action", "description"]

    def get_action(self, obj):
        return obj.get_action_flag_display()

    def get_description(self, obj):
        return obj.get_change_message()
