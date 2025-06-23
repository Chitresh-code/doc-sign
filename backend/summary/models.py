from django.db import models
from documents.models import GeneratedDocument

class DocumentSummary(models.Model):
    document = models.OneToOneField(GeneratedDocument, on_delete=models.CASCADE, related_name='summary')
    
    terms = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    dates = models.JSONField(blank=True, null=True)  # e.g. { "effective": "...", "expiration": "..." }
    signatures_required = models.JSONField(blank=True, null=True)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for Document {self.document.id}"