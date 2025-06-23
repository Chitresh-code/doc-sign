from django.urls import path
from signature.views import SignDocumentView, ViewSignedPDFView

urlpatterns = [
    path('sign/<int:pk>/', SignDocumentView.as_view(), name='sign-document'),
    path('view/<int:pk>/', ViewSignedPDFView.as_view(), name='view-signed-pdf'),
]