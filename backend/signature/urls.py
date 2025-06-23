from django.urls import path
from signature.views import SignDocumentView, ViewSignedPDFView, SignedStatusView

urlpatterns = [
    path('sign/<int:pk>/', SignDocumentView.as_view(), name='sign-document'),
    path('view/<int:pk>/', ViewSignedPDFView.as_view(), name='view-signed-pdf'),
    path('status/<int:pk>/', SignedStatusView.as_view(), name='signed-status'),
]