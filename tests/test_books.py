import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from routers.books import create_and_update_book_transaction
from config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        test_client.headers.update({"X-API-Key": settings.api_key})
        yield test_client
    app.dependency_overrides.clear()


def test_create_and_update_book_transaction(db_session):
    result = create_and_update_book_transaction(
        title="Initial Title",
        description="Test description",
        new_title="Updated Title",
        db=db_session
    )

    assert result.title == "Updated Title"
    assert result.description == "Test description"
    assert result.id is not None

    from models import Book
    book = db_session.query(Book).filter(Book.id == result.id).first()
    assert book is not None
    assert book.title == "Updated Title"


def test_create_book_api(client):
    response = client.post(
        "/books/",
        json={"title": "Test Book", "description": "A test book"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["description"] == "A test book"
    assert "id" in data
    assert "created_at" in data


def test_get_books_list(client):
    client.post("/books/", json={"title": "Book 1", "description": "First book"})
    client.post("/books/", json={"title": "Book 2", "description": "Second book"})

    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    response = client.get("/books/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    response = client.get("/books/?title=Book 1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Book 1"


def test_get_single_book(client):
    create_response = client.post(
        "/books/",
        json={"title": "Single Book", "description": "A single book"}
    )
    book_id = create_response.json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Book"
    assert data["id"] == book_id

    response = client.get("/books/999")
    assert response.status_code == 404


def test_update_book(client):
    create_response = client.post(
        "/books/",
        json={"title": "Original Title", "description": "Original description"}
    )
    book_id = create_response.json()["id"]

    response = client.put(
        f"/books/{book_id}",
        json={"title": "Updated Title", "description": "Updated description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"

    response = client.put("/books/999", json={"title": "New Title"})
    assert response.status_code == 404


def test_delete_book(client):
    create_response = client.post(
        "/books/",
        json={"title": "To Delete", "description": "This will be deleted"}
    )
    book_id = create_response.json()["id"]

    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404

    response = client.delete("/books/999")
    assert response.status_code == 404


def test_duplicate_title_error(client):
    client.post("/books/", json={"title": "Unique Book", "description": "First"})

    response = client.post("/books/", json={"title": "Unique Book", "description": "Second"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
