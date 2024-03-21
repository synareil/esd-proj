# consumer.py
import pika
from database import SessionLocal, ErrorLog
import os, sys, json

def insert_error_log(message, source):
    db_session = SessionLocal()
    try:
        new_log = ErrorLog(message=message, source=source)
        db_session.add(new_log)
        db_session.commit()
    finally:
        db_session.close()

def on_message(channel, method_frame, header_frame, body):
    message = json.loads(body) 
    message_text = message['message']
    source = message['source']

    insert_error_log(message_text, source)
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

def start_consuming():
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    
    # Form the RabbitMQ connection URL
    rabbitmq_url = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}{RABBITMQ_VHOST}'

    queue_name = 'error_logs'

    parameters = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message)

    sys.stdout.write('Waiting for messages. To exit press CTRL+C\n')
    channel.start_consuming()
    
if __name__ == "__main__":
    start_consuming()
        