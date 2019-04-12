from rest_framework import serializers


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
