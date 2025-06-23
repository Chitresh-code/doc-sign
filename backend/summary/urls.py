from django.urls import path
from summary.views import GenerateDocumentSummaryView, ViewDocumentSummaryView

urlpatterns = [
    path('generate/<int:pk>/', GenerateDocumentSummaryView.as_view(), name='generate-summary'),
    path('view/<int:pk>/', ViewDocumentSummaryView.as_view(), name='view-summary'),
]