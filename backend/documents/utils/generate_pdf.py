from xhtml2pdf import pisa
import tempfile

def generate_pdf_from_html(html_content: str) -> bytes:
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    with open(output.name, "wb") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)

    with open(output.name, "rb") as f:
        return f.read()