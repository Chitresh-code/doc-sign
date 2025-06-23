from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt

class GeneratedDocument(models.Model):
    DOCUMENT_TYPES = [
        ('nda', 'NDA'),
        ('invoice', 'Invoice'),
        ('offer', 'Offer Letter'),
    ]
    
    name = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents_to_sign')

    plain_pdf = models.FileField(upload_to='documents/plain/')
    encrypted_pdf = models.FileField(upload_to='documents/encrypted/')

    encrypted_metadata = encrypt(models.JSONField(null=True, blank=True))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document_type} by {self.owner.username} for {self.signer.username if self.signer else 'N/A'}"