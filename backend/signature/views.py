from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from documents.models import GeneratedDocument
from signature.models import SignedDocument
from documents.utils import render_html, generate_pdf
from signature.utils.decrypt import decrypt_value
from django.http import FileResponse
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

class SignDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            doc = get_object_or_404(GeneratedDocument, pk=pk)

            if doc.signer != request.user:
                return Response({'error': 'You are not authorized to sign this document.'}, status=403)

            if hasattr(doc, 'signed_version'):
                return Response({'error': 'This document has already been signed.'}, status=400)

            # Load the encrypted metadata
            metadata = {
                k: decrypt_value(str(v))
                for k, v in doc.encrypted_metadata.items()
            }

            # Add signer info
            signer_name = f"{request.user.first_name} {request.user.last_name}".strip()
            metadata['signature_text'] = f"Signed by {signer_name}"
            plain_metadata = {k: decrypt_value(v) for k, v in doc.encrypted_metadata.items()}
            plain_metadata['signature_text'] = f"Signed by {signer_name}"
            
            TEMPLATE_MATCH = {
                'nda': 'nda',
                'invoice': 'invoice',
                'offer': 'offer_letter',
            }
            template_name = TEMPLATE_MATCH.get(doc.document_type, 'default_template')
            template = f"{template_name}.html"

            # Generate signed HTML → PDF
            html_signed = render_html.render_html(template, plain_metadata)
            signed_pdf = generate_pdf.generate_pdf_from_html(html_signed)

            html_signed_enc = render_html.render_html(template, metadata)
            signed_pdf_enc = generate_pdf.generate_pdf_from_html(html_signed_enc)

            # Save new signed document
            signed = SignedDocument.objects.create(
                original_document=doc,
                signed_by=request.user
            )
            cleaned_name = ''.join(c for c in doc.name if c.isalnum() or c in (' ', '_')).rstrip()
            signed.signed_pdf.save(f"{cleaned_name}_signed.pdf", ContentFile(signed_pdf))
            signed.signed_encrypted_pdf.save(f"{cleaned_name}_signed_encrypted.pdf", ContentFile(signed_pdf_enc))

            # Notify owner
            send_mail(
                subject=f"Document Signed: {doc.name or doc.document_type}",
                message=f"{signer_name} has signed your document: {doc.name or doc.document_type}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[doc.owner.email],
                fail_silently=True
            )

            logger.info(f"Document {doc.id} signed by {request.user.username}")
            return Response({'message': 'Document signed successfully.'}, status=201)

        except Exception as e:
            logger.error(f"[SignDocumentView] Error: {str(e)}", exc_info=True)
            return Response({'error': 'Failed to sign the document.'}, status=500)

class ViewSignedPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        doc = get_object_or_404(GeneratedDocument, pk=pk)

        if doc.owner != request.user and doc.signer != request.user:
            return Response({'error': 'Unauthorized'}, status=403)

        if not hasattr(doc, 'signed_version'):
            return Response({'error': 'Signed document not found.'}, status=404)

        return FileResponse(doc.signed_version.signed_pdf.open('rb'), content_type='application/pdf')

class SignedStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        doc = get_object_or_404(GeneratedDocument, pk=pk)
        try:
            signed_doc = SignedDocument.objects.get(original_document=doc)
            return Response({
                'signed': True,
                'signed_at': signed_doc.signed_at,
                'signed_by': signed_doc.signed_by.username
            })
        except SignedDocument.DoesNotExist:
            return Response({'signed': False})