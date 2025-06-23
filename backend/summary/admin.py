from django.contrib import admin
from .models import DocumentSummary

@admin.register(DocumentSummary)
class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ('document', 'generated_at')
    search_fields = ('document__name',)
    readonly_fields = ('generated_at',)
    fieldsets = (
        (None, {
            'fields': ('document',)
        }),
        ('Summary Details', {
            'fields': ('terms', 'responsibilities', 'dates', 'signatures_required')
        }),
        ('Timestamps', {
            'fields': ('generated_at',)
        }),
    )