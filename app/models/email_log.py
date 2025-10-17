from datetime import datetime
from app import db

class EmailLog(db.Model):
    __tablename__ = "email_logs"
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("donations.id"), nullable=False)
    recipient = db.Column(db.String(255), nullable=False)
    pdf_path = db.Column(db.String(500))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="sent")  # sent / failed
    error_message = db.Column(db.Text, nullable=True)