# Habits Tracker

A FastAPI-based habit tracking application with user authentication, habit management, and analytics.

## Features

- User registration and authentication (JWT)
- Create, read, update, and delete habits
- Track habit completions
- Analytics including:
  - Current streak
  - Longest streak
  - Completion rate
  - Average completion time
  - Weekly and monthly statistics

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite with SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Migrations**: Alembic
- **Testing**: pytest

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:
```bash
pytest
```

## Project Structure

```
habits_tracker/
├── api/v1/              # API endpoints
├── core/                # Security and JWT utilities
├── db/                  # Database models and session
├── schemas/             # Pydantic schemas
├── services/            # Business logic
├── tests/               # Tests
├── alembic/             # Database migrations
└── main.py              # FastAPI application
```
