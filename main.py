"""FastAPI application entry point."""
from fastapi import FastAPI
from database import engine, Base
from routers import books
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book API",
    description="A simple CRUD API for managing books",
    version="1.0.0"
)

# Include routers
app.include_router(books.router)


@app.on_event("startup")
def create_tables():
    """Create database tables on application startup."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        # Don't raise - allow app to start even if tables exist or connection fails
        # Tables will be created on first request if connection works


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to the Book API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
