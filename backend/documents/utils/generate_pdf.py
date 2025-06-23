import pdfkit
import tempfile

def generate_pdf_from_html(html_content) -> bytes:
    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as output:
        pdfkit.from_string(html_content, output.name)
        return output.read()