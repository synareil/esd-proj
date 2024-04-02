from fastapi import FastAPI, Depends, HTTPException, Response
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
QUEUE_NAME = "Search.error"

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

KONG_GATEWAY = "http://kong:8000"
CART_BASEURL = f"{KONG_GATEWAY}/cart"
INVENTORY_BASEURL = f"{KONG_GATEWAY}/item"
ORDER_BASEURL = f"{KONG_GATEWAY}/order"
SHIPPING_BASEURL  = f"{KONG_GATEWAY}/shipping"
RECOMMENDATION_BASEURL = f"{KONG_GATEWAY}/recommendation"
# RECOMMENDATION_BASEURL = f"http://localhost:9001"

app = FastAPI()

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

    routing_key = 'Search.error'
    
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
            except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException) as e:
                print(f"Request failed: {e}. Retrying in {delay} seconds.")
                await asyncio.sleep(delay)
                
        try:
            return await client.request(method, url, **kwargs)
        except (httpx.RequestError):
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class Item(BaseModel):
    name: str = Field(min_length=3)
    description: str = Field(min_length=3)
    category: str = Field(min_length=3)
    
class SearchRequest(BaseModel):
    user_id: int
    
@app.get("/health", status_code=status.HTTP_200_OK)
async def check_health():
    return None

@app.get("/search", status_code=status.HTTP_200_OK)
async def search(q: str, user_id: int):
    to_return = {}

    #call inventory microservice
    url = f"{INVENTORY_BASEURL}/search?q={q}"
    inventory_response = await call_service_with_retry(method = "GET", url=url)
    if inventory_response.status_code != 200:
        message = {'message':"Invetory service failed. " + inventory_response.text, 'source':"Search"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=inventory_response.status_code, detail=inventory_response.text)
    
    to_return["search"] = inventory_response.json()
    
    # Call the cart
    url = f"{CART_BASEURL}/{user_id}"
    headers = {"Content-Type": "application/json"}
    cart_response = await call_service_with_retry(method='GET', url=url, headers=headers)
    
    if cart_response.status_code != 202 and cart_response.status_code != 404:
        message = {'message':"Cart service failed. " + cart_response.text, 'source':"Search"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=cart_response.status_code, detail="Cart service failed")
    else:
        # Call the inventory microservice
        items_list = cart_response.json()["data"]
        items = []
        for item in items_list:
            itemID = item["itemID"]
        
            url = f"{INVENTORY_BASEURL}/{itemID}"
            inventory_response = await call_service_with_retry(method = "GET", url=url)
            if inventory_response.status_code == 200:
                inventory_response = inventory_response.json()["data"]
                itemModel = Item(name=inventory_response["name"],
                                    description=inventory_response["description"],
                                    category=inventory_response["category"])
                items.append(itemModel.model_dump())
            
        #Call Recommendation microservice
        url = f"{RECOMMENDATION_BASEURL}/recommend"
        payload = {"items": items}
        recommendation_response = await call_service_with_retry(method = "POST", url=url, json=payload)
        if recommendation_response.status_code != 200:
            message = {'message':"Recommendation service failed. " + recommendation_response.text, 'source':"Search"}
            send_to_rabbitmq(message)
            raise HTTPException(status_code=recommendation_response.status_code, detail=recommendation_response.text)
        
        to_return["recommendation"] = recommendation_response.json()["items"]
    
    return to_return
            
        