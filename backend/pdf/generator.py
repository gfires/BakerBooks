from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import os

FONT_PATH = os.path.join(os.path.dirname(__file__), "templates", "fonts", "AguafinaScript-Regular.ttf")
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('AguafinaScript', FONT_PATH))
    SIGNATURE_FONT = 'AguafinaScript'
else:
    SIGNATURE_FONT = 'Helvetica-Oblique'  # Fallback

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "blank_affidavit.pdf")

def parse_cardholder_name(full_name: str) -> str:
    """Extract first two words from cardholder name.
    Example: 'Gavin Firestone (Treasurer)' -> 'Gavin Firestone'
    """
    words = full_name.strip().split()
    return ' '.join(words[:2]) if len(words) >= 2 else full_name

def generate_affidavit(
    vendor: str,
    price: float,
    date: str,
    cardholder_name: str
) -> BytesIO:

    template_pdf = PdfReader(TEMPLATE_PATH)
    output_pdf = PdfWriter()

    overlay = BytesIO()
    c = canvas.Canvas(overlay, pagesize=letter)

    parsed_name = parse_cardholder_name(cardholder_name)
    expense_date = datetime.fromisoformat(date).strftime("%m/%d/%Y")
    receipt_details = f"{vendor}, ${price:.2f}, {expense_date}"
    today_date = datetime.now().strftime("%m/%d/%Y")

    c.setFont("Helvetica", 14)
    c.drawString(60, 562, receipt_details)

    c.setFont(SIGNATURE_FONT, 16)
    c.drawString(64, 120, parsed_name)

    c.setFont("Helvetica", 14)
    c.drawString(348, 120, today_date)

    c.save()

    overlay.seek(0)
    overlay_pdf = PdfReader(overlay)

    page = template_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    output_pdf.add_page(page)

    output = BytesIO()
    output_pdf.write(output)
    output.seek(0)

    return output
