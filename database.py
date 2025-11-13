"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import getpass

# Get database URL from environment variable
# If not set, you need to configure it with your PostgreSQL credentials
# Example: export DATABASE_URL="postgresql://username:password@localhost:5432/bookdb"
DATABASE_URL = None

if not DATABASE_URL:
    # Try to use system user with localhost (may require password)
    default_user = getpass.getuser()
    DATABASE_URL = f"postgresql://postgres:oniel123@127.0.0.1:5433/bookdb"
    print(f"Warning: DATABASE_URL not set. Using default: {DATABASE_URL}")
    print("If this fails, set DATABASE_URL environment variable with your credentials.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
