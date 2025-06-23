from rest_framework import serializers
from documents.models import GeneratedDocument, NDADraft

class DocumentGenerateSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=GeneratedDocument.DOCUMENT_TYPES)
    recipient_name = serializers.CharField()
    role = serializers.CharField(required=False)
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    start_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

class GeneratedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedDocument
        fields = '__all__'
        
class NDADraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = NDADraft
        fields = '__all__'
        read_only_fields = ['created_by', 'ai_clause_details', 'confirmed_at']