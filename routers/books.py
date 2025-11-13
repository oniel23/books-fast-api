"""API routes for book operations."""
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
    """
    Business logic function that demonstrates transaction handling.
    Creates a book and immediately updates it in a single transaction.
    
    Args:
        title: Initial book title
        description: Book description
        new_title: New title to update to
        db: Database session
        
    Returns:
        Updated book object
        
    Raises:
        Exception: If any operation fails, transaction is rolled back
    """
    try:
        # Create book
        new_book = Book(title=title, description=description)
        db.add(new_book)
        db.flush()  # Flush to get the ID without committing
        
        # Update book in same transaction
        new_book.title = new_title
        db.commit()
        db.refresh(new_book)
        return new_book
    except Exception as e:
        db.rollback()
        raise e


@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Create a new book.
    
    Args:
        book: Book data to create
        db: Database session
        
    Returns:
        Created book object
        
    Raises:
        HTTPException: If book with same title already exists
    """
    # Check if book with same title already exists
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
    """
    Get list of books with pagination and optional filtering.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        title: Optional title filter (partial match)
        db: Database session
        
    Returns:
        List of book objects
    """
    query = db.query(Book)
    
    # Custom SQL query: Filter by title if provided (case-insensitive partial match)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    
    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """
    Get a single book by ID.
    
    Args:
        book_id: ID of the book to retrieve
        db: Database session
        
    Returns:
        Book object
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    """
    Update a book by ID.
    
    Args:
        book_id: ID of the book to update
        book_update: Updated book data
        db: Database session
        
    Returns:
        Updated book object
        
    Raises:
        HTTPException: If book not found or title already exists
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if new title conflicts with existing book
    if book_update.title and book_update.title != book.title:
        existing_book = db.query(Book).filter(Book.title == book_update.title).first()
        if existing_book:
            raise HTTPException(status_code=400, detail="Book with this title already exists")
    
    # Update fields
    if book_update.title is not None:
        book.title = book_update.title
    if book_update.description is not None:
        book.description = book_update.description
    
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Delete a book by ID.
    
    Args:
        book_id: ID of the book to delete
        db: Database session
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    return None


@router.get("/stats/count", response_model=dict)
def get_book_count(db: Session = Depends(get_db)):
    """
    Get total count of books using a custom SQL aggregation query.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with total book count
    """
    # Custom SQL query: Count all books using aggregation
    count = db.query(func.count(Book.id)).scalar()
    return {"total_books": count}

