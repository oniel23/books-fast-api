# Book API - FastAPI CRUD Application

A simple FastAPI application that provides CRUD operations for managing books, backed by PostgreSQL database.

## Features

- RESTful API endpoints for book management
- PostgreSQL database with SQLAlchemy ORM
- Request/response validation using Pydantic
- Pagination and filtering support
- Transaction handling
- Unit and integration tests

## Project Structure

```
.
├── main.py              # FastAPI application entry point
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic schemas for validation
├── routers/
│   └── books.py         # Book API routes
├── tests/
│   └── test_books.py    # Unit and integration tests
└── requirements.txt     # Python dependencies
```

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Install Dependencies

Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

### 2. Database Setup

#### Install PostgreSQL

If PostgreSQL is not installed, install it:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

#### Create Database

Start PostgreSQL service and create a database:

```bash
# Start PostgreSQL service (if not running)
sudo service postgresql start  # Linux
# or
brew services start postgresql  # macOS
```

**Option 1: Using default postgres user (Recommended for development)**

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql  # Linux
# or
psql -U postgres  # macOS/Windows (may prompt for password)

# If you need to set/reset the postgres password:
ALTER USER postgres WITH PASSWORD 'postgres';

# Create database
CREATE DATABASE bookdb;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bookdb TO postgres;
\q
```

**Option 2: Create a new user**

```bash
# Connect to PostgreSQL
sudo -u postgres psql  # Linux

# Create a new user and database
CREATE USER bookuser WITH PASSWORD 'bookpass';
CREATE DATABASE bookdb OWNER bookuser;
GRANT ALL PRIVILEGES ON DATABASE bookdb TO bookuser;
\q
```

#### Configure Database Connection

Set the database URL as an environment variable:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/bookdb"
```

Or create a `.env` file in the project root:

```bash
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bookdb" > .env
```

**If you're using a different user/password:**
```bash
DATABASE_URL=postgresql://bookuser:bookpass@localhost:5432/bookdb
```

### 3. Run Database Migrations

The application will automatically create tables on first run using `Base.metadata.create_all()` in `main.py`.

### 4. Configure API Key (Optional)

The application uses a simple API key for securing book endpoints.

- Default API key: `secret-key`
- Header name: `X-API-Key`

To change the API key, set the `API_KEY` environment variable or add it to `.env`:

```bash
echo "API_KEY=your-secret-key" >> .env
```

### 5. Run the Application (Local Python)

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## API Endpoints

All `/books` endpoints require the `X-API-Key` header.

### Create Book
- **POST** `/books/`
- Request body:
  ```json
  {
    "title": "Book Title",
    "description": "Book description"
  }
  ```
- Headers:
  - `X-API-Key: secret-key`
- Response: `201 Created` with book object

### Get Books List
- **GET** `/books/`
- Query parameters:
  - `skip` (int, default: 0): Number of records to skip
  - `limit` (int, default: 10, max: 100): Maximum records to return
  - `title` (string, optional): Filter by title (partial match)
- Example: `GET /books/?skip=0&limit=10&title=python`
- Headers:
  - `X-API-Key: secret-key`
- Response: `200 OK` with list of books

### Get Single Book
- **GET** `/books/{id}`
- Response: `200 OK` with book object or `404 Not Found`
- Headers:
  - `X-API-Key: secret-key`

### Update Book
- **PUT** `/books/{id}`
- Request body (all fields optional):
  ```json
  {
    "title": "Updated Title",
    "description": "Updated description"
  }
  ```
- Headers:
  - `X-API-Key: secret-key`
- Response: `200 OK` with updated book object or `404 Not Found`

### Delete Book
- **DELETE** `/books/{id}`
- Response: `204 No Content` or `404 Not Found`
- Headers:
  - `X-API-Key: secret-key`

### Get Book Count
- **GET** `/books/stats/count`
- Response: `200 OK` with total book count
- Headers:
  - `X-API-Key: secret-key`

## Testing

Run tests using pytest:

```bash
pytest tests/ -v
```

> **Note:** Tests automatically set the API key header using the default value (`secret-key`).

## Running with Docker

### Build Docker Image

```bash
docker build -t book-api .
```

Run the container locally:

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/bookdb \
  -e API_KEY=secret-key \
  book-api
```

> When using `docker run`, make sure PostgreSQL is reachable at the provided `DATABASE_URL`. On Linux you may need to replace `host.docker.internal` with the host IP address.

### Run with Docker Compose

The repository includes a `docker-compose.yml` file that starts both the API and PostgreSQL database.

```bash
docker compose up --build
```

This command will:
- Build the API image
- Start PostgreSQL with default credentials (`postgres` / `postgres`)
- Set the API key from the `API_KEY` environment variable (defaults to `secret-key`)
- Expose the API on `http://localhost:8000`

To override the API key when using compose:

```bash
API_KEY=my-secret docker compose up --build
```

Press `Ctrl+C` to stop the containers. To remove them:

```bash
docker compose down
```

> The PostgreSQL data is persisted in the `postgres_data` volume. Remove it with `docker compose down -v` if you need a clean slate.

The test suite includes:
- Unit test for transaction handling business logic
- Integration tests for all API endpoints
- Error handling tests (404, 400)

Tests use SQLite in-memory database for faster execution.

## Code Features

### Database Model
- **Book** model with fields:
  - `id`: Primary key (auto-increment)
  - `title`: String (unique, required, indexed)
  - `description`: Text (optional)
  - `created_at`: DateTime (auto-generated)

### Custom SQL Queries
- Title filtering using `ilike` for case-insensitive partial matching
- Aggregation query for counting total books using `func.count()`

### Transaction Handling
- `create_and_update_book_transaction()` function demonstrates creating and updating a book in a single transaction with rollback on error

### Error Handling
- 404 for missing resources
- 400 for validation errors (duplicate titles)
- Proper HTTP status codes throughout

## Development Notes

- The code follows a modular structure with separate files for models, schemas, and routes
- Pydantic schemas ensure request/response validation
- Database sessions are managed using FastAPI dependencies
- All endpoints include docstrings for documentation

## Troubleshooting

### Database Connection Issues

If you get connection errors:

1. **Check PostgreSQL is running:**
   ```bash
   sudo service postgresql status
   ```

2. **Verify database exists:**
   ```bash
   sudo -u postgres psql -l
   ```

3. **Check connection string:**
   Make sure your `DATABASE_URL` environment variable or `.env` file has the correct format:
   ```
   postgresql://username:password@localhost:5432/database_name
   ```

### Authentication Issues

If you get password authentication errors:

1. **Reset postgres user password:**
   ```bash
   sudo -u postgres psql
   ALTER USER postgres WITH PASSWORD 'postgres';
   \q
   ```

2. **Check PostgreSQL authentication config:**
   ```bash
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   ```
   Ensure the line for local connections uses `md5`:
   ```
   local   all             all                                     md5
   host    all             all             127.0.0.1/32            md5
   ```
   Then restart PostgreSQL:
   ```bash
   sudo service postgresql restart
   ```

## License

This project is created for assignment purposes.

