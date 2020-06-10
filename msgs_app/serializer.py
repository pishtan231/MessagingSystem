from rest_framework import serializers


class FormSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=256)
    body = serializers.CharField(max_length=256)
