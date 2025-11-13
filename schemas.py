from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    description: Optional[str] = Field(None, description="Book description")


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class BookResponse(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

