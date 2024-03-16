from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from typing import Annotated
from pydantic import BaseModel, Field
from starlette import status
from datetime import datetime
from models import MarketingContent
import pika, json
import os

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def send_to_rabbitmq(message: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,
                                           port=RABBITMQ_PORT,
                                           virtual_host=RABBITMQ_VHOST,
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Ensure the queue exists
    queue_name = 'marketingContentQueue'
    channel.queue_declare(queue=queue_name, durable=True)

    # Publish message
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=json.dumps(message),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    connection.close()

class Item(BaseModel):
    title: str
    desc: str
    price: float
    image: str

class NewItemMarketingRequest(BaseModel):
    title: str
    desc: str
    item1: Item
    item2: Item
    item3: Item


class MarketingContentRequest(BaseModel):
    title: str = Field(min_length=3)
    content_type: str = Field(min_length=3)
    content_body: str = Field(min_length=3)
    tags: str = Field(min_length=3, default=None)


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(MarketingContent).all()

@app.post("/marketingcontent", status_code=status.HTTP_201_CREATED)
async def create_marketing(db: db_dependency, marketingContent_request: MarketingContentRequest):
    marketingcontent_model = MarketingContent(**marketingContent_request.model_dump())

    db.add(marketingcontent_model)
    db.commit()
    db.refresh(marketingcontent_model)

    message = {
        # Assuming these are the fields you want to send
        "id": marketingcontent_model.id,
        "title": marketingcontent_model.title,
        "content_type": marketingcontent_model.content_type,
        "content_body": marketingcontent_model.content_body,
        "status": marketingcontent_model.status,
        "created_at": marketingcontent_model.created_at.isoformat(),
        "tags": marketingcontent_model.tags,
    }

    try:
        send_to_rabbitmq(message)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return marketingcontent_model


@app.post("/marketingcontent/newitem", status_code=status.HTTP_201_CREATED)
async def create_marketing(newItem_request: NewItemMarketingRequest):
    message = newItem_request.model_dump()

    send_to_rabbitmq(message)

    return newItem_request