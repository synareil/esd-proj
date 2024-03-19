# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, ErrorLog
from starlette import status
from typing import Annotated

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/errors/", status_code=status.HTTP_200_OK)
def read_errors(db: db_dependency):
    errors = db.query(ErrorLog).all()
    return errors
