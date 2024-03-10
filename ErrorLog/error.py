#!/usr/bin/env python3
import amqp_connection
import json
import pika
import docker #need download
# from app import create_error_log
#from os import environ

e_queue_name = 'Error'        # queue to be subscribed by Error microservice

# Instead of hardcoding the values, we can also get them from the environ as shown below
# e_queue_name = environ.get('Error') #Error

def receiveError(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=e_queue_name, on_message_callback=callback, auto_ack=True)
        print('error microservice: Consuming from queue:', e_queue_name)
        channel.start_consuming() # an implicit loop waiting to receive messages; 
        #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"error microservice: Failed to connect: {e}") 

    except KeyboardInterrupt:
        print("error microservice: Program interrupted by user.")

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nerror microservice: Received an error by " + __file__)

############################################################
    #for microname in microservices:
        #check_and_restart_container(microname)
        #check if all the containers is up and running
        # else it would restart it
############################################################

    processError(body)
    print()

def processError(errorMsg):
    print("error microservice: Printing the error message:")
    try:
        error = json.loads(errorMsg)
        print("--JSON:", error)
        create_error_log(error['Date'], error['Time'], error['Desc'], error['Microservice'])
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", errorMsg)
    print()

#only test this when we done with the project based 3 scenarios.
def check_and_restart_container(container_name):
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
        if container.status != 'running':
            print(f"Microservice {container_name} is down. Restarting...")
            container.restart()
            print(f"Microservice {container_name} has been restarted.")
    except docker.errors.NotFound:
        print(f"No such container: {container_name}")
    except docker.errors.APIError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__": # execute this program only if it is run as a script (not by 'import')    
    print("error microservice: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("error microservice: Connection established successfully")
    channel = connection.channel()
    receiveError(channel)
