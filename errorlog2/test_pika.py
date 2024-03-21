import pika,json

credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters(host='localhost',
                                        port=5672,
                                        virtual_host='/',
                                        credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Make sure the queue exists. This matches the consumer setup.
channel.queue_declare(queue='error_logs', durable=True)

# Your error message
error_message = {'source': "Wakwawwwws", 'message':"ohno"}
body=json.dumps(error_message)

# Publish the message to the queue
channel.basic_publish(
    exchange='',
    routing_key='error_logs',
    body=json.dumps(error_message),
    properties=pika.BasicProperties(
        delivery_mode=2,  # Makes the message persistent
    )
)

print(" [x] Sent 'Example error message here'")

# Close the connection
connection.close()
