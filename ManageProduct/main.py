from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, List
from pydantic import BaseModel, Field
from starlette import status
import pika, json
import os
from time import time
import httpx
import asyncio
import async_timeout

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/") 
QUEUE_NAME = "ProductManageme.error"

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,
                                        port=RABBITMQ_PORT,
                                        virtual_host=RABBITMQ_VHOST,
                                        credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare a topic exchange
exchange_name = 'topic_logs'
channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

# Declare the consumer's queue
queue_name = 'error_logs'
channel.queue_declare(queue=queue_name, durable=True)

# Bind the queue to the exchange with a pattern that matches any '.error' routing key
binding_key = '*.error'
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=binding_key)
connection.close()

KONG_GATEWAY = "http://localhost:8000"
CART_BASEURL = f"{KONG_GATEWAY}/cart"
INVENTORY_BASEURL = f"{KONG_GATEWAY}/item"
ORDER_BASEURL = f"{KONG_GATEWAY}/order"
SHIPPING_BASEURL  = f"{KONG_GATEWAY}/shipping"

app = FastAPI()

def generate_idempotency_key(user_id: str) -> str:
    return f"{user_id}-{int(time() * 1000)}"

def send_to_rabbitmq(message: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,
                                           port=RABBITMQ_PORT,
                                           virtual_host=RABBITMQ_VHOST,
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    exchange_name = 'topic_logs'
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

    routing_key = 'PlaceOrder.error'
    
    channel.basic_publish(exchange=exchange_name, 
                          routing_key=routing_key, 
                          body=json.dumps(message),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    connection.close()
    
async def call_service_with_retry(method: str, url: str, retries: int = 3, backoff_factor: float = 2.0, **kwargs):
    """
    Makes an HTTP request using the specified method, with retry logic.

    :param method: HTTP method (e.g., 'get', 'post', 'put', 'delete').
    :param url: URL to the endpoint.
    :param retries: Number of retries.
    :param backoff_factor: Backoff factor for retries.
    :param kwargs: Additional arguments to pass to httpx request (e.g., json, headers).
    """
    retry_delays = [backoff_factor ** i for i in range(retries)]
    async with httpx.AsyncClient() as client:
        for delay in retry_delays:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                print(f"Request failed: {e}. Retrying in {delay} seconds.")
                await asyncio.sleep(delay)
        # Final attempt without catching the exception
        return await client.request(method, url, **kwargs)

class Item(BaseModel):
    itemID: int
    salesPrice: float

class SalesRequest(BaseModel):
    items: List[Item]

@app.get("/health", status_code=status.HTTP_200_OK)
async def check_health():
    return None

@app.post("/sales", status_code=status.HTTP_200_OK)
async def add_item(salesRequest: SalesRequest):
    
    #call inventory microservice
    for item in salesRequest.items:
        itemID = item.itemID
        salesPrice = item.salesPrice
        
        url = f"{INVENTORY_BASEURL}/{itemID}"   
        headers = {"Content-Type": "application/json"}
        payload = {'salesPrice': salesPrice}
        inventory_response = await call_service_with_retry(method = "PUT", url=url, json=payload)  
        
        if inventory_response.status_code != 200:
            raise HTTPException(status_code=inventory_response.status_code, detail=inventory_response.text)
       
       
    #call cart microservice
    user_item = {}
    for item in salesRequest.items:
        itemID = item.itemID
        url = f"{CART_BASEURL}/item/{itemID}"   
        headers = {"Content-Type": "application/json"}
        
        cart_response = await call_service_with_retry(method = "GET", url=url, json=payload) 
        users = items = cart_response.json()["data"]
        for user in users:
            if user not in user_item:
                user_item[user] = [itemID]
            else:
                user_item[user].append(itemID)
        if cart_response.status_code != 202:
            raise HTTPException(status_code=cart_response.status_code, detail=cart_response.text)
    
     
        