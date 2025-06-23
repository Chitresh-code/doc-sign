from django.contrib import admin
from documents.models import GeneratedDocument


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'document_type', 'owner', 'signer', 'created_at')
    search_fields = ('name', 'owner__username', 'signer__username')
    list_filter = ('document_type', 'created_at')
    readonly_fields = ('plain_pdf', 'encrypted_pdf', 'encrypted_metadata', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'document_type', 'owner', 'signer') 
        }),
        ('Files', {
            'fields': ('plain_pdf', 'encrypted_pdf')
        }),
        ('Metadata', {
            'fields': ('encrypted_metadata',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )