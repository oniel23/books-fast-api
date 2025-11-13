"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Base schema for Book with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    description: Optional[str] = Field(None, description="Book description")


class BookCreate(BookBase):
    """Schema for creating a new book."""
    pass


class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class BookResponse(BookBase):
    """Schema for book response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

