from django.db import models
from django.conf import settings
from documents.models import GeneratedDocument

class SignedDocument(models.Model):
    original_document = models.OneToOneField(GeneratedDocument, on_delete=models.CASCADE, related_name='signed_version')
    signed_pdf = models.FileField(upload_to='documents/signed/')
    signed_encrypted_pdf = models.FileField(upload_to='documents/signed_encrypted/')
    signed_at = models.DateTimeField(auto_now_add=True)
    signed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Signed copy of {self.original_document.name}"
