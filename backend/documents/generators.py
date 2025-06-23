from django.template.loader import render_to_string
from weasyprint import HTML
import os
from django.conf import settings


def generate_pdf(document_type: str, context: dict, filename: str) -> str:
    html_string = render_to_string(f"documents/{document_type}.html", context)
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'generated_docs', filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    HTML(string=html_string).write_pdf(pdf_path)
    return f"generated_docs/{filename}"

def require_fields(data, fields):
    missing = [field for field in fields if data.get(field) in (None, '')]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

def get_context(document_type: str, data: dict, user) -> dict:
    if document_type == 'offer_letter':
        require_fields(data, ['recipient_name', 'role', 'salary', 'start_date'])
        return {
            "recipient_name": data["recipient_name"],
            "role": data["role"],
            "salary": data["salary"],
            "start_date": data["start_date"],
            "signature": None,
            "issuer": user.username,
        }

    elif document_type == 'nda':
        require_fields(data, ['recipient_name', 'start_date', 'due_date'])
        return {
            "recipient_name": data["recipient_name"],
            "start_date": data["start_date"],
            "end_date": data["due_date"],
            "signature": None,
            "issuer": user.username,
        }

    elif document_type == 'invoice':
        require_fields(data, ['recipient_name', 'item', 'description', 'amount', 'due_date'])
        return {
            "recipient_name": data["recipient_name"],
            "item": data["item"],
            "description": data["description"],
            "amount": data["amount"],
            "due_date": data["due_date"],
            "signature": None,
            "issuer": user.username,
        }

    else:
        raise ValueError(f"Unsupported document type: {document_type}")