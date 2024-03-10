import pika, json, requests, os

import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

# Configure API key authorization: api-key
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'

def callback(ch, method, properties, body):
    # Process the message
    message = json.loads(body)
    print(f"Received message: {message}")
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    to = [{"email":"julian.maximal@gmail.com","name":"Julian Willis"}]
    headers = {"Some-Custom-Name":"unique-id-1234"}
    template_id = 3
    params = message
    headers={"X-Mailin-custom": "custom_header_1:custom_value_1|custom_header_2:custom_value_2|custom_header_3:custom_value_3", "charset": "iso-8859-1"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers, template_id=template_id,params=params)
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

    # Acknowledge that the message has been processed
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    
    # Form the RabbitMQ connection URL
    rabbitmq_url = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}{RABBITMQ_VHOST}'

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
