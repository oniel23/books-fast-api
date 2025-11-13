from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from database import get_db
from models import Book
from schemas import BookCreate, BookUpdate, BookResponse
from dependencies import verify_api_key

router = APIRouter(
    prefix="/books",
    tags=["books"],
    dependencies=[Depends(verify_api_key)],
)


def create_and_update_book_transaction(title: str, description: str, new_title: str, db: Session):
    try:
        new_book = Book(title=title, description=description)
        db.add(new_book)
        db.flush()
        new_book.title = new_title
        db.commit()
        db.refresh(new_book)
        return new_book
    except Exception as e:
        db.rollback()
        raise e


@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    existing_book = db.query(Book).filter(Book.title == book.title).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="Book with this title already exists")

    db_book = Book(title=book.title, description=book.description)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=List[BookResponse])
def get_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    title: Optional[str] = Query(None, description="Filter by title (partial match)"),
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))

    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_update.title and book_update.title != book.title:
        existing_book = db.query(Book).filter(Book.title == book_update.title).first()
        if existing_book:
            raise HTTPException(status_code=400, detail="Book with this title already exists")

    if book_update.title is not None:
        book.title = book_update.title
    if book_update.description is not None:
        book.description = book_update.description

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return None


@router.get("/stats/count", response_model=dict)
def get_book_count(db: Session = Depends(get_db)):
    count = db.query(func.count(Book.id)).scalar()
    return {"total_books": count}

