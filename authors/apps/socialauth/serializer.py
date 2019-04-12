from rest_framework import serializers


class SocialSerializer(serializers.Serializer):
    backend = serializers.CharField()
    access_token = serializers.CharField()
