from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class MarketingContent(Base):
    __tablename__ = 'marketing_contents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)  
    content_type = Column(String)
    content_body = Column(Text)  
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)  
    tags = Column(String)
