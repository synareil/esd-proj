from fastapi import FastAPI, Depends, HTTPException, Response
from typing import Annotated
from pydantic import BaseModel, Field
from starlette import status
import pika, json
import os
from time import time
import httpx
import asyncio
import async_timeout
import stripe
from fastapi.middleware.cors import CORSMiddleware

stripe.api_key = os.getenv("STRIPE_API_KEY","sk_test_51Ov2FCHr2KXuSharY9xOCUwZA46HDdAMWpWvblgstDH6LMPpo2rSbh3tcy2ts0wTD4LBJeR0Fv1BOON6dXANDiS20027koww3v")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/") 
QUEUE_NAME = "PlaceOrder.error"

import pika
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

KONG_GATEWAY = "http://kong:8000"
CART_BASEURL = f"{KONG_GATEWAY}/cart"
INVENTORY_BASEURL = f"{KONG_GATEWAY}/item"
ORDER_BASEURL = f"{KONG_GATEWAY}/order"
SHIPPING_BASEURL  = f"{KONG_GATEWAY}/shipping"
YOUR_DOMAIN = 'http://localhost:8000/placeorder'

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class CheckoutRequest(BaseModel):
    user_id: int
    shippingAddress: str = Field(min_length=3)
    
class CheckoutNextRequest(BaseModel):
    order_id: int
    user_id: int
    shippingAddress: str = Field(min_length=3)

class CustomResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text
        
def generate_idempotency_key(user_id: str) -> str:
    return f"{user_id}-{int(time() * 1000)}"

async def rollback_inventory(items):
    payload = {"checkout": items}
    url = f"{INVENTORY_BASEURL}/checkout/rollback"
    inventory_response = await call_service_with_retry(method = "POST", url=url, json=payload)
    print("Rollbacking inventory ...")
    
    if inventory_response.status_code != 200:
        message = {'message':"Rollbacking Inventory service failed" + inventory_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)

async def rollback_order(orderID):
    url = f"{ORDER_BASEURL}/{orderID}"
    order_response = await call_service_with_retry(method = "DELETE", url=url)
    print("Rollbacking order ...")
    
    if order_response.status_code != 200:
        message = {'message':"Rollbacking order service failed" + order_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)

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
            except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException) as e:
                print(f"Request failed: {e}. Retrying in {delay} seconds.")
                await asyncio.sleep(delay)
                
        try:
            return await client.request(method, url, **kwargs)
        except (httpx.RequestError):
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

@app.get("/health", status_code=status.HTTP_200_OK)
async def check_health():
    return None

@app.post("/checkout", status_code=status.HTTP_200_OK)
async def orchestrate_microservices(checkoutRequest: CheckoutRequest):
    user_id = checkoutRequest.user_id
    shippingAddress = checkoutRequest.shippingAddress
    idempotency_key = generate_idempotency_key(user_id)
    
    # Call the cart
    url = f"{CART_BASEURL}/{user_id}"
    headers = {"Content-Type": "application/json"}
    cart_response = await call_service_with_retry(method='GET', url=url, headers=headers)
    
    if cart_response.status_code != 202:
        message = {'message':"Cart service failed. " + cart_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=cart_response.status_code, detail="Cart service failed")
    
    # Call the inventory microservice
    items = cart_response.json()["data"]
    for item in items:
        del item["cartID"]
    payload = {"checkout": items}
    url = f"{INVENTORY_BASEURL}/checkout"
    inventory_response = await call_service_with_retry(method = "POST", url=url, json=payload)
    
    if inventory_response.status_code != 200:
        message = {'message':"Inventory service failed. " + inventory_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=inventory_response.status_code, detail="Inventory service failed")
    
    
    # Call the order microservice
    payload = {
        "userID": user_id,
        "status": "created",
        "items": items
        }
    url= f"{ORDER_BASEURL}"
    order_response = await call_service_with_retry(method = "POST", url=url, json=payload)
    
    if order_response.status_code != 201:
        message = {'message':"Order service failed. " + order_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)
        await rollback_inventory(items)
        raise HTTPException(status_code=order_response.status_code, detail="Order service failed")


    # Call Stripe
    orderID = order_response.json()["data"]["orderID"]
    totalPrice = inventory_response.json()["data"]["totalPrice"]
    name = "Order #" + str(orderID)
    product = stripe.Product.create(name=name,
                                    default_price_data={"unit_amount": 1,
                                                        "currency": "sgd",
                                                        },
                                    expand=["default_price"],
                                    )

    price = stripe.Price.create(product=product.id,
                                unit_amount=int(totalPrice * 100),
                                currency="sgd",
                                )

    session = stripe.checkout.Session.create(
                                             line_items=[{"price": price.id, "quantity": 1}],
                                             mode="payment",
                                             success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
                                             cancel_url=YOUR_DOMAIN + '/cancel?session_id={CHECKOUT_SESSION_ID}',
                                             metadata={"orderID":str(orderID),"userID":str(user_id),"shippingAddress":shippingAddress}
                                             )

    # response = Response()
    # response.status_code = 303
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Location"] = session.url
    # return response
    
    return session.url


@app.get("/success", status_code=status.HTTP_200_OK)
async def finish_checkout(session_id):
    
    session = stripe.checkout.Session.retrieve(session_id)
    
    orderID = session.metadata.orderID
    user_id = session.metadata.userID
    shippingAddress = session.metadata.shippingAddress
    
    # Call the cart
    url = f"{CART_BASEURL}/{user_id}"
    headers = {"Content-Type": "application/json"}
    cart_response = await call_service_with_retry(method='GET', url=url, headers=headers)
    
    if cart_response.status_code != 202:
        message = {'message':"Cart service failed. " + cart_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=cart_response.status_code, detail="Cart service failed")
    items = cart_response.json()["data"]
    for item in items:
        del item["cartID"]   
    
    # Call the shipping microservice
    payload = {
        "OrderID": orderID,
        "UserID": user_id,
        "shippingAddress": shippingAddress,
        "ShippingStatus": "Order proccessing"
        }
    url= f"{SHIPPING_BASEURL}/createshipping"
    shipping_response = await call_service_with_retry(method = "POST", url=url, json=payload)
    
    if shipping_response.status_code != 201:
        message = {'message':"Shipping service failed. " + shipping_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=shipping_response.status_code, detail="Shipping service failed")
    
    # Close the cart
    url= f"{CART_BASEURL}/close/{user_id}"
    cart_response = await call_service_with_retry(method = "POST", url=url)
    
    if cart_response.status_code != 204:
        message = {'message':"Cart service failed. " + cart_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=cart_response.status_code, detail="Cart service failed")
    
    response = Response()
    response.status_code = 303
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Location"] = "http://localhost:8008/success.html"
    return response

@app.get("/cancel", status_code=status.HTTP_200_OK)
async def cancel_checkout(session_id):
    
    session = stripe.checkout.Session.retrieve(session_id)
    
    orderID = session.metadata.orderID
    user_id = session.metadata.userID
    shippingAddress = session.metadata.shippingAddress
    
    # Call the cart
    url = f"{CART_BASEURL}/{user_id}"
    headers = {"Content-Type": "application/json"}
    cart_response = await call_service_with_retry(method='GET', url=url, headers=headers)
    
    if cart_response.status_code != 202:
        message = {'message':"Cart service failed. " + cart_response.text, 'source':"PlaceOrder"}
        send_to_rabbitmq(message)
        raise HTTPException(status_code=cart_response.status_code, detail="Cart service failed")
    items = cart_response.json()["data"]
    for item in items:
        del item["cartID"]   
    
    # Rollback the services
    await rollback_inventory(items)
    await rollback_order(orderID)

    # response = Response()
    # response.status_code = 200
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Location"] = "http://localhost:8008/failure.html"
    # return response
    
