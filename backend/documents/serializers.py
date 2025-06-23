from rest_framework import serializers
from users.models import User
from documents.models import GeneratedDocument
from signature.models import SignedDocument


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
    signed = serializers.SerializerMethodField()
    signed_at = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedDocument
        fields = [
            'id', 'name', 'document_type', 'plain_pdf', 'encrypted_pdf',
            'encrypted_metadata', 'signer', 'owner', 'created_at', 'signed', 'signed_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'plain_pdf', 'encrypted_pdf']

    def get_signed(self, obj):
        return hasattr(obj, 'signed_version')

    def get_signed_at(self, obj):
        if hasattr(obj, 'signed_version'):
            return obj.signed_version.signed_at
        return None


class GeneratedDocumentListSerializer(serializers.ModelSerializer):
    signer_username = serializers.CharField(source='signer.username', read_only=True)
    signed = serializers.SerializerMethodField()
    signed_at = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedDocument
        fields = ['id', 'name', 'document_type', 'signer_username', 'created_at', 'signed', 'signed_at']

    def get_signed(self, obj):
        return hasattr(obj, 'signed_version')

    def get_signed_at(self, obj):
        if hasattr(obj, 'signed_version'):
            return obj.signed_version.signed_at
        return None