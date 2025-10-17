import json
import pika

def enqueue_donation(donation_id, email):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='donation_tasks', durable=True)
    
    message = json.dumps({"donation_id": donation_id, "email": email})
    channel.basic_publish(
        exchange='',
        routing_key='donation_tasks',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    connection.close()