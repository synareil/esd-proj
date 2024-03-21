from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, ErrorLog
from starlette import status
from typing import Annotated
from contextlib import asynccontextmanager
import threading
import consumer  # Import the consumer module

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/", status_code=status.HTTP_200_OK)
def read_errors(db: db_dependency):
    errors = db.query(ErrorLog).all()
    return errors

# Function to run the consumer in a background thread
def run_consumer_thread():
    thread = threading.Thread(target=consumer.start_consuming)
    thread.daemon = True  # Daemonize thread
    thread.start()

@app.on_event("startup")
def startup_event():
    run_consumer_thread()  # Ensure this is called when the app starts