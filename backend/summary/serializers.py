from rest_framework import serializers
from summary.models import DocumentSummary

class DocumentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSummary
        fields = ['terms', 'responsibilities', 'dates', 'signatures_required', 'generated_at']