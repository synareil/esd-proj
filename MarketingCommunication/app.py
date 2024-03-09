import pika, json, requests, os

def callback(ch, method, properties, body):
    # Process the message
    message = json.loads(body)
    print(f"Received message: {message}")
    
    # try:
    #     api_response = requests.post(message['url'], json=message['data'])
    #     if api_response.status_code == 200:
    #         print("Successfully called API and processed message.")
    #     else:
    #         print(f"API call failed with status code: {api_response.status_code}, details: {api_response.text}")
    # except Exception as e:
    #     print(f"Error during API call: {e}")

    # Acknowledge that the message has been processed
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    
    # Form the RabbitMQ connection URL
    rabbitmq_url = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}'

    queue_name = 'marketingContentQueue'

    parameters = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    start_consuming()
