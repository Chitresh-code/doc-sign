import uuid
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from documents.serializers import DocumentGenerateSerializer, GeneratedDocumentSerializer
from documents.generators import generate_pdf, get_context
from documents.models import GeneratedDocument
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from documents.models import NDADraft
from documents.generators import generate_nda_terms
from documents.serializers import NDADraftSerializer
from datetime import datetime


class DocumentGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentGenerateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            document_type = data["document_type"]
            try:
                context = get_context(document_type, data, request.user)
            except ValueError as ve:
                return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

            # Generate unique file name
            filename = f"{document_type}_{uuid.uuid4().hex}.pdf"
            relative_path = generate_pdf(document_type, context, filename)

            # Save to DB
            doc = GeneratedDocument.objects.create(
                created_by=request.user,
                document_type=document_type,
                file=relative_path,
                metadata=context,
            )

            return Response(GeneratedDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DocumentListView(ListAPIView):
    serializer_class = GeneratedDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GeneratedDocument.objects.filter(created_by=self.request.user)


class DocumentPreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        doc = get_object_or_404(GeneratedDocument, pk=pk, created_by=request.user)
        return FileResponse(doc.file, content_type='application/pdf')
    
class NDADraftGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Prompt is required."}, status=400)

        # Call LLM (OpenAI, etc.) to generate content
        ai_content = generate_nda_terms(prompt)

        draft = NDADraft.objects.create(
            created_by=request.user,
            prompt=prompt,
            ai_clause_details=ai_content
        )
        return Response(NDADraftSerializer(draft).data, status=201)


class NDADraftConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        draft = get_object_or_404(NDADraft, pk=pk, created_by=request.user)
        new_content = request.data.get("ai_clause_details")
        if new_content:
            draft.ai_clause_details = new_content
        draft.is_confirmed = True
        draft.confirmed_at = datetime.now()
        draft.save()
        return Response(NDADraftSerializer(draft).data)