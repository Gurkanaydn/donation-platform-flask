import os
import ssl
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
import os

load_dotenv()


class EmailService:
    def __init__(self):
        self.sender_email = os.getenv("SMTP_SENDER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))

        self.context = ssl.create_default_context()
        self.server = None

    def connect(self):
        #SMTP bağlantısı.
        if not self.server:
            self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=self.context)
            self.server.login(self.sender_email, self.password)
            print("SMTP bağlantısı kuruldu.")

    def send_email(self, to_email, subject, body, attachment_path=None):
        self.connect()

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Pdf kontrolü
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                message.attach(part)

        text = message.as_string()
        try:
            self.server.sendmail(self.sender_email, to_email, text)
            print(f"Mail gönderildi: {to_email}")
        except smtplib.SMTPException as e:
            print(f"Mail gönderim hatası: {e}")
        print(f"E-posta gönderildi: {to_email}")

    def close(self):
        if self.server:
            self.server.quit()
            self.server = None
            print("SMTP bağlantısı kapatıldı.")
