from pdf_generator import generate_pdf
from email_service import EmailService
import os
import sys
import json
import asyncio
import aio_pika

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app, db
from app.models.donation import Donation
from app.models.email_log import EmailLog

app = create_app()
email_service = EmailService()


async def process_donation_message(body):
    with app.app_context():
        data = json.loads(body)
        donation_id = data.get("donation_id")
        _email = data.get("email")

        donation = db.session.get(Donation, donation_id)
        if not donation:
            print(f"- Donation ID {donation_id} bulunamadı.")
            return

        _pdf_path = await asyncio.to_thread(generate_pdf, donation)
        print(f"- PDF oluşturuldu: {_pdf_path}")

        await asyncio.to_thread(
            email_service.send_email,
            _email,
            f"Bağış Makbuzu #{donation_id}",
            "Makbuzunuz ekte yer almaktadır.",
            _pdf_path
        )
        print("- E-posta gönderildi")

        donation.status = "processed"

        email_log = EmailLog(
            donation_id=donation_id,
            recipient=_email,
            pdf_path=_pdf_path,
        )
        db.session.add(email_log)

        db.session.commit()
        print("- Donation başarıyla işlendi ve veritabanı güncellendi.")


async def start_worker():
    
    r_user = os.getenv("RABBITMQ_USER")
    r_password = os.getenv("RABBITMQ_PASSWORD")
    r_host = os.getenv("RABBITMQ_HOST")

    rabbitmq_url = f"amqp://{r_user}:{r_password}@{r_host}"
    queue_name = "donation_tasks"

    connection = await aio_pika.connect_robust(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await process_donation_message(message.body)


if __name__ == "__main__":
    asyncio.run(start_worker())