from fastapi import FastAPI, Depends, HTTPException, Response
from typing import Annotated, List
from pydantic import BaseModel, Field
from starlette import status
import httpx
import asyncio
import pika
import os, json

KONG_GATEWAY = "http://kong:8000"
INVENTORY_BASEURL = f"{KONG_GATEWAY}/item"

app = FastAPI()

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/") 
QUEUE_NAME = "Search.error"

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,port=RABBITMQ_PORT,virtual_host=RABBITMQ_VHOST,credentials=credentials)
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

def send_to_rabbitmq(message: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,port=RABBITMQ_PORT,virtual_host=RABBITMQ_VHOST,credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    exchange_name = 'topic_logs'
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

    routing_key = 'Recommendation.error'
    
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(message),properties=pika.BasicProperties(delivery_mode=2,))
    # make message persistent
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

class RecommendationRequest(BaseModel):
    items: List[Item]
    
@app.get("/health", status_code=status.HTTP_200_OK)
async def check_health():
    return None

@app.post("/recommend", status_code=status.HTTP_200_OK)
async def add_item(recommendationRequest: RecommendationRequest):
    if recommendationRequest.items == []:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item list is empty")
    
    item1 = recommendationRequest.items
    item1 = item1[0]
    category = item1.category
    
    #call item microservice
    url = f"{INVENTORY_BASEURL}/?category={category}"
    inventory_response = await call_service_with_retry(method = "GET", url=url)
    if inventory_response.status_code != 200:
        message = {'message':"Inventory service failed. ", 'source':"Recommendation"}
        send_to_rabbitmq(message)
        
        raise HTTPException(status_code=inventory_response.status_code)
    
    return inventory_response.json()["data"]