from django.contrib import admin
from .models import SignedDocument

@admin.register(SignedDocument)
class SignedDocumentAdmin(admin.ModelAdmin):
    list_display = ('original_document', 'signed_at', 'signed_by')
    search_fields = ('original_document__name', 'signed_by__username')
    readonly_fields = ('signed_pdf', 'signed_encrypted_pdf', 'signed_at')
    fieldsets = (
        (None, {
            'fields': ('original_document', 'signed_by')
        }),
        ('Signed Files', {
            'fields': ('signed_pdf', 'signed_encrypted_pdf')
        }),
        ('Timestamps', {
            'fields': ('signed_at',)
        }),
    )