from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['circle', 'student', 'payment_amount', 'pdf']

class DocumentSignSerializer(serializers.Serializer):
    signed = serializers.BooleanField()
