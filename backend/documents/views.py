from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.db.models import Q

from users.models import User
from documents.models import GeneratedDocument
from documents.serializers import (
    DocumentCreateSerializer,
    GeneratedDocumentSerializer,
    GeneratedDocumentListSerializer
)

from documents.utils import render_html, generate_pdf, encryption, ai
from rest_framework.generics import ListAPIView
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.crypto import get_random_string
from decouple import config

import logging
logger = logging.getLogger(__name__)


class GenerateDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = DocumentCreateSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning("Invalid document creation data", extra={'errors': serializer.errors})
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            TEMPLATES_MATCH = {
                'nda': 'nda',
                'invoice': 'invoice',
                'offer': 'offer_letter',
            }
            matching_template = TEMPLATES_MATCH.get(data['template_type'])
            template = f"{matching_template}.html"

            signer, created = User.objects.get_or_create(
                username=data['signer_username'],
                defaults={
                    'email': data['signer_email'],
                    'first_name': data['signer_first_name'],
                    'last_name': data['signer_last_name'],
                    'role': 'signer',
                    'password': get_random_string(12),
                }
            )
            if created:
                logger.info(f"Signer created: {signer.username}")

            context = " ".join([str(v) for v in data['metadata'].values()])
            ai_content = ai.generate_ai_clause(data['prompt'], context)
            metadata = {**data['metadata'], 'ai_clause_details': ai_content, 'issuer': request.user.get_full_name()}

            html_plain = render_html.render_html(template, metadata)
            pdf_plain = generate_pdf.generate_pdf_from_html(html_plain)

            encrypted_metadata = {
                k: encryption.encrypt_value(str(v)) for k, v in metadata.items()
            }
            html_encrypted = render_html.render_html(template, encrypted_metadata)
            pdf_encrypted = generate_pdf.generate_pdf_from_html(html_encrypted)

            doc = GeneratedDocument.objects.create(
                owner=request.user,
                signer=signer,
                document_type=data['template_type'],
                name=data.get('name', f"{data['template_type'].capitalize()} Document"),
                encrypted_metadata=encrypted_metadata
            )
            clean_name = data.get("name", f"{data['template_type'].capitalize()} Document").replace(" ", "_")
            doc.plain_pdf.save(f"{clean_name}.pdf", ContentFile(pdf_plain))
            doc.encrypted_pdf.save(f"{clean_name}_encrypted.pdf", ContentFile(pdf_encrypted))
            doc.plain_html.save(f"{clean_name}.html", ContentFile(html_plain.encode('utf-8')))
            doc.encrypted_html.save(f"{clean_name}_encrypted.html", ContentFile(html_encrypted.encode('utf-8')))

            logger.info(f"Document generated: {doc.id} by {request.user.username}")
            return Response(GeneratedDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"[GenerateDocumentView] Error: {str(e)}", exc_info=True)
            return Response({'error': 'Something went wrong while generating the document.'}, status=500)


class GeneratedDocumentListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratedDocumentListSerializer

    def get_queryset(self):
        return GeneratedDocument.objects.filter(owner=self.request.user).order_by('-created_at')


class GeneratedDocumentServeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            document = get_object_or_404(
                GeneratedDocument,
                Q(owner=request.user) | Q(signer=request.user),
                pk=pk,
            )

            if not document.plain_pdf:
                return Response({'error': 'PDF not available'}, status=status.HTTP_404_NOT_FOUND)

            return FileResponse(document.plain_pdf.open('rb'), content_type='application/pdf')

        except Exception as e:
            logger.error(f"[ServeDocument] Failed to serve PDF for document {pk}: {str(e)}", exc_info=True)
            return Response({'error': 'Failed to serve the document PDF.'}, status=500)
        

class SendToSignerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            document = get_object_or_404(GeneratedDocument, pk=pk, owner=request.user)

            if not document.signer:
                return Response({'error': 'No signer associated with this document.'}, status=400)

            signer_email = document.signer.email
            document_name = document.name or f"{document.document_type.capitalize()} Document"
            signer_name = f"{document.signer.first_name} {document.signer.last_name}".strip()

            # Generate token and build frontend URL
            token = str(AccessToken.for_user(document.signer))
            frontend_base_url = config("FRONTEND_URL", default="https://your-frontend.com")
            sign_url = f"{frontend_base_url}/sign?token={token}&doc={document.id}"

            email_subject = f"Document to Sign: {document_name}"
            email_body = f"""
            Hi {signer_name or document.signer.username},

            You have received a document titled **{document_name}** to review and sign.

            Please click the link below to access the document:
            {sign_url}

            Thank you.
            """

            email = EmailMessage(
                subject=email_subject,
                body=email_body,
                to=[signer_email],
            )

            if document.plain_pdf and document.plain_pdf.path:
                email.attach_file(document.plain_pdf.path)

            email.send()
            logger.info(f"Sent document {document.id} to signer {document.signer.username}")
            return Response({'message': 'Document sent to signer successfully.'})

        except Exception as e:
            logger.error(f"[SendToSignerView] Error: {str(e)}", exc_info=True)
            return Response({'error': 'Failed to send document to signer.'}, status=500)
