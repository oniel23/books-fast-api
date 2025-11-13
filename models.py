"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Book(Base):
    """Book model representing a book in the database."""
    
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

