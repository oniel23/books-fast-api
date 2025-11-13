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

app.include_router(books.router)


@app.on_event("startup")
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")


@app.get("/")
def root():
    return {"message": "Welcome to the Book API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
