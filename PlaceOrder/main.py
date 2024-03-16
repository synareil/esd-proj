from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel, Field
from starlette import status
import pika, json
import os
import requests
from requests.exceptions import HTTPError, RequestException

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/") 
QUEUE_NAME = "PlaceOrder.error"

KONG_GATEWAY = "http://localhost:8000"
CART_BASEURL = f"{KONG_GATEWAY}/cart"
INVENTORY_BASEURL = f"{KONG_GATEWAY}/item"
ORDER_BASEURL = f"{KONG_GATEWAY}/order"



app = FastAPI()

def send_to_rabbitmq(message: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,
                                           port=RABBITMQ_PORT,
                                           virtual_host=RABBITMQ_VHOST,
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    queue_name = QUEUE_NAME
    channel.queue_declare(queue=queue_name, durable=True)

    # Publish message
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=json.dumps(message),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    connection.close()
    
@app.get("/health", status_code=status.HTTP_200_OK)
async def check_health():
    return None

@app.post("/checkout/{user_id}", status_code=status.HTTP_201_CREATED)
async def checkout_user_cart(user_id: int):
    
    #GET ITEM IN USER CART
    try:
        url = f"{CART_BASEURL}/{user_id}"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        
        items = response.json()["data"]
        for item in items:
            del item["cartID"]
        print(items)
    except HTTPError as http_err:
        raise HTTPException(status_code=404, detail='Cart not found')
    except RequestException as err:
        raise HTTPException(status_code=503, detail='Cart service is not available')

    #MINUS OFF THE INVENTORY
    payload = {"checkout": items}
    try:
        response = requests.post(f"{INVENTORY_BASEURL}/checkout", json=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        raise HTTPException(status_code=404, detail='Item not found')
    except RequestException as err:
        raise HTTPException(status_code=503, detail='Cart service is not available')
    
    #CREATE ORDER
    payload = {
        "userID": user_id,
        "status": "created",
        "items": items
        }
    try:
        response = requests.post(f"{ORDER_BASEURL}", json=payload)
        response.raise_for_status()
    except HTTPError as http_err:
        raise HTTPException(status_code=404, detail='Internal Server Error')
    except RequestException as err:
        raise HTTPException(status_code=503, detail='Cart service is not available')