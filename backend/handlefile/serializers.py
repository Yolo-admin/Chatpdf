from rest_framework import serializers
from .models import UploadedPDF

class UploadedPDFSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UploadedPDF
        fields = ['id', 'file', 'uploaded_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['file'] = instance.file.name.split('/')[-1] if instance.file else ""
        return rep