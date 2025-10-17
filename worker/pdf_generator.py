from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "receipts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# para birimi db'den alınabilir.

def generate_pdf(donation):
    receipt_path = os.path.join(OUTPUT_DIR, f"receipt_{donation.id}.pdf")
    c = canvas.Canvas(receipt_path, pagesize=A4)
    c.drawString(65, 800, "XXX VAKFI - BAĞIŞ MAKBUZU / XXX FOUNDATION - DONATION RECEIPT")
    c.drawString(50, 760, f"Makbuz No / Receipt No: {donation.id}")
    c.drawString(50, 740, f"Kampanya / Campaign: {donation.campaign.title}")
    c.drawString(50, 720, f"Tutar / Amount: {donation.amount} TRY")
    c.drawString(50, 700, f"Bagis Tarihi / Donation Date: {donation.created_at.strftime('%d.%m.%Y %H:%M')}")
    c.drawString(50, 680, f"Durum / Status: {donation.status}")
    c.showPage()
    c.save()

    print(f"✅ PDF makbuzu oluşturuldu: {receipt_path}")
    return receipt_path
