from django.db import models
from users.models import User

class GeneratedDocument(models.Model):
    DOCUMENT_TYPES = [
        ('offer_letter', 'Offer Letter'),
        ('nda', 'Non-Disclosure Agreement'),
        ('invoice', 'Invoice'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='generated_docs/')
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} for {self.created_by.username}"
    
class NDADraft(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    ai_clause_details = models.TextField()
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NDA Draft by {self.created_by.username}"