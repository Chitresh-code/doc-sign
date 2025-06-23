from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from summary.models import DocumentSummary
from documents.models import GeneratedDocument
from summary.serializers import DocumentSummarySerializer
from summary.utils.summarizer import summarize_encrypted_html
import logging

logger = logging.getLogger(__name__)

class GenerateDocumentSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            doc = get_object_or_404(GeneratedDocument, pk=pk)

            if doc.signer != request.user:
                return Response({'error': 'You are not authorized to summarize this document.'}, status=403)

            if hasattr(doc, 'summary'):
                return Response({'message': 'Summary already exists for this document.'}, status=400)

            html_path = doc.encrypted_pdf.path.replace(".pdf", ".html")
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    encrypted_html = f.read()
            except FileNotFoundError:
                return Response({'error': 'Encrypted HTML not found.'}, status=404)

            result = summarize_encrypted_html(encrypted_html)

            if "error" in result:
                return Response(result, status=500)

            summary = DocumentSummary.objects.create(
                document=doc,
                terms=result.get("terms", ""),
                responsibilities=result.get("responsibilities", ""),
                dates=result.get("dates", {}),
                signatures_required=result.get("signatures_required", []),
            )

            logger.info(f"Generated summary for document {doc.id}")
            return Response(DocumentSummarySerializer(summary).data, status=201)

        except Exception as e:
            logger.error(f"[GenerateDocumentSummaryView] {str(e)}", exc_info=True)
            return Response({'error': 'Failed to generate summary.'}, status=500)


class ViewDocumentSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            doc = get_object_or_404(GeneratedDocument, pk=pk)

            if doc.signer != request.user:
                return Response({'error': 'Unauthorized'}, status=403)

            if not hasattr(doc, 'summary'):
                return Response({'error': 'Summary not available.'}, status=404)

            return Response(DocumentSummarySerializer(doc.summary).data)

        except Exception as e:
            logger.error(f"[ViewDocumentSummaryView] {str(e)}", exc_info=True)
            return Response({'error': 'Failed to retrieve summary.'}, status=500)