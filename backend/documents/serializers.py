from rest_framework import serializers
from users.models import User
from documents.models import GeneratedDocument


class DocumentCreateSerializer(serializers.Serializer):
    template_type = serializers.ChoiceField(choices=['nda', 'offer', 'invoice'])
    prompt = serializers.CharField()
    metadata = serializers.DictField()

    signer_username = serializers.CharField()
    signer_email = serializers.EmailField()
    signer_first_name = serializers.CharField()
    signer_last_name = serializers.CharField()
    name = serializers.CharField(required=False)


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedDocument
        fields = [
            'id', 'name', 'document_type', 'plain_pdf', 'encrypted_pdf',
            'encrypted_metadata', 'signer', 'owner', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'plain_pdf', 'encrypted_pdf']


class GeneratedDocumentListSerializer(serializers.ModelSerializer):
    signer_username = serializers.CharField(source='signer.username', read_only=True)

    class Meta:
        model = GeneratedDocument
        fields = ['id', 'name', 'document_type', 'signer_username', 'created_at']