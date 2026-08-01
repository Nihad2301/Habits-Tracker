# Habits Tracker API

A backend API for tracking daily habits, streaks, and completion analytics — built with FastAPI, PostgreSQL, and JWT authentication.

## Tech Stack

- **FastAPI** — web framework
- **PostgreSQL** (production) / **SQLite** (local development) — database
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **JWT (python-jose)** — authentication
- **Resend** — transactional email (verification, password reset)
- **Docker** + **Docker Compose** — containerization for local development
- **Railway** — deployment
- **pytest** — testing
- **ruff** — linting
- **GitHub Actions** — CI/CD

## Getting Started

### Local development (Docker)

```bash
docker-compose up
```

This starts both the API and a local PostgreSQL instance, wired together automatically.

### Local development (without Docker)

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in your own values
alembic upgrade head
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Running tests

```bash
python -m pytest
```

### Linting

```bash
ruff check .
```

## Architecture & Design Decisions

This section covers the *why* behind the structure, not just the *what* — the reasoning mattered more than the code during development.

### Layered architecture: routers vs. services

Routers handle HTTP concerns only — receiving requests and returning responses. All business logic (validation, database operations, orchestration) lives in service functions. This keeps routers thin and, more importantly, keeps business logic decoupled from FastAPI itself — a service function like `register_user()` has no idea it's being called from a web API. It could be called from a CLI script, a background job, or a test, and it would behave identically.

### Centralized exception handling

Instead of raising `HTTPException` throughout the codebase, the app defines a custom exception hierarchy (`AppException` and its subclasses — `WeakPasswordError`, `NotFoundError`, `AlreadyExistsError`, `EmailDeliveryError`, etc.), each carrying its own `status_code` and `default_message`. These are plain Python exceptions with zero dependency on FastAPI.

A small set of centralized exception handlers (`custom_exception_handler`, `validation_exception_handler`, `jwt_exception_handler`) is the *only* place in the app that translates an internal exception into an HTTP response. This means:

- Adding a new error type takes one line, with no router changes required
- Every error response — regardless of source (business logic, request validation, JWT decoding) — comes back in the same predictable shape
- Business logic stays fully decoupled from the web layer

### Authentication: JWT + database-backed one-time tokens

Two different token strategies are used deliberately, for two different problems:

**JWT (login sessions):** a signed, stateless token. The payload (user ID, expiry) is Base64-encoded, not encrypted — it's readable by anyone, and that's fine, because the security guarantee comes from the **signature**, not secrecy of the payload. The server recomputes the signature on each request using `SECRET_KEY`; if it doesn't match, the token is rejected. No database lookup is needed for every request, since the token verifies itself.

**Email verification / password reset tokens:** random, single-use strings stored as database rows, each tracking `is_used` and `expires_at`. Unlike a JWT, there's no cryptographic proof to check — the database *is* the proof. These are marked used immediately after a successful verification/reset specifically to prevent replay: a reset link sitting in an email inbox (which can be compromised, forwarded, or accessed later) should only ever be valid for a single use.

### Configuration and secrets

All configuration is centralized in a single `config.py` (`Settings` class), which reads from environment variables with sane local defaults. The rest of the app imports `settings` and never touches `os.getenv` directly. This decouples the app from *how* configuration is sourced — switching from `.env` files to a secrets manager later would mean changing one file, not fifteen.

Secrets (`SECRET_KEY`, `RESEND_API_KEY`, `DATABASE_URL`) live only in environment variables — `.env` locally (gitignored), Railway's environment variables in production. `.env.example` documents which variables exist with placeholder values, without exposing anything real.

Local development uses SQLite for simplicity; production uses PostgreSQL, set via `DATABASE_URL`. Migrations are managed with Alembic against whichever database is active.

### Email configuration (Resend)

The app uses Resend for transactional emails (email verification, password reset). **Important note:** The current configuration uses Resend's free tier, which only allows sending emails to the account holder's verified email address. This is suitable for development and personal testing.

To send emails to arbitrary users (for production use), you would need to:
1. Verify a custom domain in Resend (e.g., `yourdomain.com`)
2. Update the `from` address in `services/email_service.py` to use your verified domain
3. Ensure your `RESEND_API_KEY` has the appropriate permissions

For now, the app is configured to send emails only to the developer's email address for testing purposes.

### Database design

- **Relationships** (`relationship()`) between `User`, `Habit`, and `HabitCompletion` avoid manual re-querying to access related data.
- **Composite unique constraint** on `HabitCompletion` (`habit_id`, `user_id`, `completion_date`) enforces "one completion per habit per user per day" at the database level — the natural place for this business rule, rather than relying solely on application-level checks that could be bypassed by a race condition or a bug elsewhere.
- **Cascade delete** (`ondelete="CASCADE"`) on foreign keys ensures that deleting a user also removes their dependent rows (habits, completions), preventing orphaned records that would otherwise cause `AttributeError`s or broken references elsewhere in the app.

### Known limitations

- **Timezone handling is global, not per-user.** All date/time boundaries (habit completion dates, streak calculations, weekly/monthly analytics) use a single app-wide timezone (`settings.TIMEZONE`), not each user's actual location. This is correct and internally consistent for a single-timezone user base, but a user in a different timezone than the configured one could see completions grouped under the wrong day. A proper fix would add a `timezone` field to `User` and use it in place of the global setting throughout `habit_completion_service.py` and `habit_analytics_service.py` — a natural extension, not implemented here to keep scope focused.

### API response consistency

Every successful response follows one of two shapes:
- `SuccessResponse` — for endpoints returning data (e.g. a created habit)
- `MessageResponse` — for endpoints with nothing to return but a confirmation (e.g. email verified)

This predictability means a frontend can write one generic response handler instead of custom parsing logic per endpoint.

### Request body vs. query parameters

Sensitive data (passwords, tokens, emails tied to a specific action) is always passed in the request body, never as a query parameter. Query parameters commonly end up logged by intermediate infrastructure (reverse proxies, load balancers, access logs) and stored in browser history — request bodies are not. This is a deliberate security choice, not just convention.

### Testing strategy

- Tests are isolated: each test runs against a fresh database state via fixtures in `conftest.py`.
- Both happy paths and edge cases are covered (expired tokens, reused tokens, duplicate usernames, unauthorized access, etc.).
- External side effects are mocked — specifically, `send_email` is mocked across the test suite so tests validate "did the app correctly attempt to send an email with the right data," without making real network calls to Resend. This keeps the suite fast, reliable, and independent of third-party service availability or API key state.

### CI/CD

Every push and pull request to `main` runs, in order: dependency install → lint (`ruff check .`) → test suite (`pytest`). A failure at either the linting or testing stage blocks the pipeline, catching issues before they reach production. Railway deploys automatically from `main` once CI passes.

## API Overview

| Area | Endpoints |
|---|---|
| Auth | register, login, logout, email verification, resend verification, password reset (request/confirm) |
| Users | profile update |
| Habits | CRUD for habits |
| Habit Completions | mark/track daily completions |
| Analytics | weekly/monthly stats, streaks |
| Health | `/health` — includes a database connectivity check |

Full interactive documentation is available at `/docs` once the app is running.