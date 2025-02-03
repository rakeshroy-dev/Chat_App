from celery import shared_task
from fpdf import FPDF
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO

@shared_task
def generate_chat_pdf(chat_messages):
    # Initialize FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add content to the PDF
    pdf.cell(200, 10, txt="Chat History", ln=True, align='C')

    for message in chat_messages:
        username = message.get('username', 'Unknown')
        content = message.get('content', '')
        timestamp = message.get('timestamp', 'N/A')
        pdf.multi_cell(0, 10, txt=f"{username}: {content} ({timestamp})")

    # Save PDF to memory
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    # Save PDF to Django's default storage
    file_name = "chat_history.pdf"
    file_path = default_storage.save(file_name, ContentFile(pdf_output.read()))
    pdf_output.close()

    return file_path