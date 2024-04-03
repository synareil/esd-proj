from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from typing import Annotated, List, Dict
from pydantic import BaseModel, Field
from starlette import status
from datetime import datetime
from models import MarketingContent, User
import pika, json
import os

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
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
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,port=RABBITMQ_PORT,virtual_host=RABBITMQ_VHOST,credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Ensure the queue exists
    queue_name = 'marketingContentQueue'
    channel.queue_declare(queue=queue_name, durable=True)

    # Publish message
    channel.basic_publish(exchange='',routing_key=queue_name,body=json.dumps(message),properties=pika.BasicProperties(delivery_mode=2,))
    # make message persistent
    connection.close()

class Item(BaseModel):
    name: str
    price: str
    image: str
    oldPrice: str
    
class UserRequest(BaseModel):
    name: str
    email: str
    
class NewSalesRequest(BaseModel):
    title: str
    items: Dict
    userItem: Dict

@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(MarketingContent).all()

@app.post("/newsales", status_code=status.HTTP_201_CREATED)
async def create_marketing(newSales_request: NewSalesRequest, db: db_dependency):
    userItem = newSales_request.userItem
    
    marketingcontent_model = MarketingContent(title = newSales_request.title, content_type="Item Sales Email")
    db.add(marketingcontent_model)
    db.commit()
    
    for userID, itemIDs in userItem.items():
        user_model = db.query(User).filter(User.id == userID).first()
        items = newSales_request.items
        
        if user_model:
            email = user_model.email
            name = user_model.name
            
            items_return = []
            for itemID in itemIDs:
                items_return.append(items[str(itemID)])
            
            message ={"to":{"email":email, "name":name},"templateId":4,"params":{"items": items_return}}
            #sample item
            # "items":[
            #         {"name": "Vinyl Sticker 1",
            #         "image": "https://i.imgur.com/lmuOVZZ.jpeg",
            #         "oldPrice": "4.30",
            #         "price": "2.00"},
            #         {"name": "Vinyl Sticker 1",
            #         "image": "https://i.imgur.com/Jt3DXDX.jpeg",
            #         "oldPrice": 4.3,
            #         "price": 2},
            #         {"name": "Vinyl Sticker 1",
            #         "image": "https://www.flickr.com/photos/184802690@N03/53600540877/",
            #         "oldPrice": 4.3,
            #         "price": 2}
            #         ]
            print(message)
            send_to_rabbitmq(message)

@app.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserRequest, db: db_dependency):
    user_model = User(**user_request.model_dump())
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    
    return user_model