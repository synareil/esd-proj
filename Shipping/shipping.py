#!/usr/bin/env python3
import amqp_connection
import json
import pika
#from os import environ


a_queue_name = 'shipping' # queue to be subscribed by Activity_Log microservice

# Instead of hardcoding the values, we can also get them from the environ as shown below
# a_queue_name = environ.get('Activity_Log') #Activity_Log

def receiveOrderLog(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=a_queue_name, on_message_callback=callback, auto_ack=True)
        print('shipping: Consuming from queue:', a_queue_name)
        channel.start_consuming()  # an implicit loop waiting to receive messages;
            #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"shipping: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("shipping: Program interrupted by user.") 


def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nshipping: Received an order by " + __file__)
    processOrder(json.loads(body))
    print()

def processOrder(order):
    print("shipping: Recording an order:")
    print(order)
    #Connect and send to Database for logging - regarding the specific details

def sendToDB(order):
    #Connect and send to Database for logging - regarding the specific details
    OrderID = order['OrderID']
    pass

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("shipping: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("shipping: Connection established successfully")
    channel = connection.channel()
    receiveOrderLog(channel)
