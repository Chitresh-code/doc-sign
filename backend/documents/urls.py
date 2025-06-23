from django.urls import path
from documents.views import (
    GenerateDocumentView,
    GeneratedDocumentListView,
    GeneratedDocumentServeView,
    SendToSignerView
)

urlpatterns = [
    path('generate/', GenerateDocumentView.as_view(), name='generate-document'),
    path('list/', GeneratedDocumentListView.as_view(), name='my-documents'),
    path('view/<int:pk>/', GeneratedDocumentServeView.as_view(), name='serve-document'),
    path('send/<int:pk>/', SendToSignerView.as_view(), name='send-to-signer'),
]