from django.urls import path
from documents.views import DocumentGenerateView, DocumentListView, DocumentPreviewView
from documents.views import NDADraftGenerateView, NDADraftConfirmView

urlpatterns = [
    path('generate/', DocumentGenerateView.as_view(), name='document-generate'),
    path('list/', DocumentListView.as_view(), name='document-list'),
    path('preview/<int:pk>/', DocumentPreviewView.as_view(), name='document-preview'),
    path('nda/generate-draft/', NDADraftGenerateView.as_view(), name='nda-draft-generate'),
    path('nda/confirm-draft/<int:pk>/', NDADraftConfirmView.as_view(), name='nda-draft-confirm'),
]