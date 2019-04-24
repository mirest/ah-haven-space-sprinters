from rest_framework import serializers
from .models import Notification
from authors.apps.articles.serializers import ArticleSerializer
from django.utils.timesince import timesince


class NotificationSerializer(serializers.ModelSerializer):

    article = ArticleSerializer('article')
    read = serializers.SerializerMethodField(method_name='read_status')
    timestance = serializers.SerializerMethodField(
        method_name='get_timesince')

    class Meta:
        """
        Notification fields to be returned to users
        """
        model = Notification
        fields = ('article', 'read', 'created_at',
                  'notification_message', 'classification',
                  'timestance')

    def read_status(self, instance):
        request = self.context.get('request')
        if request.user in instance.read_by.all():
            return True
        else:
            return False

    def get_timesince(self, instance, now=None):
        return timesince(instance.created_at, now)
