from rest_framework import serializers


class TokenSerialier(serializers.Serializer):
    token = serializers.CharField()
