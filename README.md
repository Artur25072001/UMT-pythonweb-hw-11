# UMT-pythonweb-hw-11

REST API for a contact management application built with **FastAPI**, **SQLAlchemy (async)**, **PostgreSQL**, **JWT authentication**, **Redis caching**, **Cloudinary** image upload, **email verification**, **password reset**, and **role-based access control**.

---

## 📋 Requirements

- Python ≥ 3.13
- PostgreSQL 12+ (or Docker)
- Redis 7+ (or Docker)
- Docker / Docker Compose (optional, for running PostgreSQL & Redis)

---

## ✨ Features

- 👤 **User registration & login** with JWT access tokens
- 📧 **Email confirmation** on registration (verification link by email)
- 🔑 **Password reset** — forgot-password / reset-password flow
- 🛡️ **Role-based access control** — `user` and `admin` roles (admin email auto-assigned via `ADMIN_EMAIL`)
- 📇 **Contact management** — full CRUD with search & filter
- 🎂 **Upcoming birthdays** — contacts with birthdays in the next 7 days
- 🖼️ **Avatar upload** to Cloudinary (admin-only)
- ⚡ **Redis caching** of authenticated users for fast `/users/me` lookups
- 🚦 **Rate limiting** via `slowapi` (e.g. `/users/me` is limited to 10 req/min)
- 🌐 **CORS** middleware enabled for `http://localhost:8000`
- 🗃️ **Alembic** database migrations

---

## 🚀 Setup & Run

### 1. Clone the repository

```bash
git clone https://github.com/Artur25072001/UMT-pythonweb-hw-11.git
cd UMT-pythonweb-hw-11
```

### 2. Create environment file

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual configuration (database credentials, JWT secret, email SMTP, Cloudinary keys, Redis URL, admin email).

### 3. Start PostgreSQL & Redis (via Docker)

```bash
docker compose up -d
```

This starts:

- **PostgreSQL 12** on port `5432` (using credentials from your `.env`)
- **Redis 7-alpine** on port `6379`

> **Note:** If you already have a PostgreSQL and/or Redis instance running, you can skip this step and point `DB_URL` / `REDIS_URL` to your existing services.

### 4. Install dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or using **pip** (generating a `requirements.txt` from `pyproject.toml`):

```bash
uv export --format requirements-txt > requirements.txt
pip install -r requirements.txt
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the application

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Or using **uv**:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at **http://127.0.0.1:8000**.

---

## 📖 API Documentation

Once the server is running, visit:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## 🔌 API Endpoints

### Auth (`/api/auth`)

| Method | Endpoint                   | Description                                   | Auth |
| ------ | -------------------------- | --------------------------------------------- | ---- |
| POST   | `/register`                | Register a new user, sends verification email | —    |
| POST   | `/request_email`           | Resend the email verification link            | —    |
| POST   | `/login`                   | Authenticate and receive a JWT token          | —    |
| GET    | `/confirmed_email/{token}` | Confirm email using a verification token      | —    |
| POST   | `/forgot-password`         | Request a password reset email                | —    |
| POST   | `/reset-password/{token}`  | Set a new password with a valid reset token   | —    |

### Users (`/api/users`)

| Method | Endpoint  | Description                                              | Auth           |
| ------ | --------- | -------------------------------------------------------- | -------------- |
| GET    | `/me`     | Get the current authenticated user (rate-limited 10/min) | Bearer         |
| PATCH  | `/avatar` | Upload a new avatar to Cloudinary                        | Bearer + admin |

### Contacts (`/api/contacts`)

| Method | Endpoint    | Description                                                  | Auth   |
| ------ | ----------- | ------------------------------------------------------------ | ------ |
| GET    | `/`         | List contacts (filter by `first_name`, `last_name`, `email`) | Bearer |
| GET    | `/birthday` | Contacts with birthdays in the next 7 days                   | Bearer |
| GET    | `/{id}`     | Get a single contact by ID                                   | Bearer |
| POST   | `/`         | Create a new contact                                         | Bearer |
| PUT    | `/{id}`     | Update an existing contact                                   | Bearer |
| DELETE | `/{id}`     | Delete a contact                                             | Bearer |

### Utils

| Method | Endpoint             | Description                                           | Auth |
| ------ | -------------------- | ----------------------------------------------------- | ---- |
| GET    | `/api/healthchecker` | Health check — verifies the database connection works | —    |

---

## 🗂️ Project Structure

```
├── main.py                  # FastAPI application entry point
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # PostgreSQL & Redis containers
├── .env.example             # Example environment variables
├── .gitignore
├── pyproject.toml           # Project metadata & dependencies
│
├── migrations/              # Alembic migrations
│   ├── env.py
│   ├── versions/
│   └── ...
│
├── docs/                    # Sphinx documentation sources
│   ├── conf.py
│   ├── index.rst
│   └── Makefile
│
└── src/
    ├── api/                 # Route handlers (auth, contacts, users, utils)
    ├── conf/                # Configuration (settings, rate limiter)
    ├── database/            # Database session, models, Redis client
    ├── repository/          # Data access layer
    ├── services/            # Business logic (auth, email, cache, Cloudinary, users, contacts)
    │   └── templates/       # Email HTML templates
    └── schemas.py           # Pydantic schemas
```

---

## 🔑 Environment Variables

| Variable                 | Description                                                        | Default                  |
| ------------------------ | ------------------------------------------------------------------ | ------------------------ |
| `POSTGRES_DB`            | PostgreSQL database name                                           | `contacts_db`            |
| `POSTGRES_USER`          | PostgreSQL user                                                    | `postgres`               |
| `POSTGRES_PASSWORD`      | PostgreSQL password                                                | _(required)_             |
| `DB_URL`                 | Async database connection string                                   | _(required)_             |
| `JWT_SECRET`             | Secret key for JWT signing                                         | _(required)_             |
| `JWT_ALGORITHM`          | JWT algorithm                                                      | `HS256`                  |
| `JWT_EXPIRATION_SECONDS` | Access token TTL (seconds); also used as Redis cache TTL           | `3600`                   |
| `MAIL_USERNAME`          | SMTP username (email)                                              | `example@example.com`    |
| `MAIL_PASSWORD`          | SMTP password / app password                                       | `xxxx xxxx xxxx xxxx`    |
| `MAIL_FROM`              | Sender email address                                               | `example@example.com`    |
| `MAIL_PORT`              | SMTP port                                                          | `587`                    |
| `MAIL_SERVER`            | SMTP server                                                        | `smtp.gmail.com`         |
| `MAIL_FROM_NAME`         | Sender display name                                                | `Rest API Service`       |
| `MAIL_STARTTLS`          | Enable STARTTLS                                                    | `True`                   |
| `MAIL_SSL_TLS`           | Enable SSL/TLS                                                     | `False`                  |
| `USE_CREDENTIALS`        | Use SMTP credentials                                               | `True`                   |
| `VALIDATE_CERTS`         | Validate SMTP certificates                                         | `True`                   |
| `REDIS_URL`              | Redis connection URL (used for caching authenticated users)        | `redis://localhost:6379` |
| `ADMIN_EMAIL`            | Email that automatically receives the `admin` role on registration | `admin@example.com`      |
| `CLOUDINARY_NAME`        | Cloudinary cloud name                                              | _(required for uploads)_ |
| `CLOUDINARY_API_KEY`     | Cloudinary API key                                                 | _(required for uploads)_ |
| `CLOUDINARY_API_SECRET`  | Cloudinary API secret                                              | _(required for uploads)_ |

See `.env.example` for a complete template.

---

## 🧪 Running Tests

The project ships with a comprehensive test suite, split into **unit tests** and **integration tests**.

Test files:

- **Unit tests** — `tests/test_unit_*.py` (db, cache, redis, email, upload_file)
- **Integration tests** — `tests/test_integration_*.py` (auth, contacts, users, utils)
- **Repository unit tests** — `tests/test_contact_repository_*.py`

The test suite uses an **in-memory SQLite database** and **mocked Redis** (see `tests/conftest.py`), so **no live PostgreSQL or Redis is required** to run the tests.

### Common commands

```bash
# Run the full test suite
pytest -v

# Run only unit tests
pytest tests/test_unit_*.py -v

# Run only integration tests
pytest tests/test_integration_*.py -v

# Run with coverage report
pytest --cov=src tests/
```

---

## 📚 Project Documentation (Sphinx)

The project includes auto-generated API documentation built with **Sphinx**.

```bash
cd docs
make html
# Open docs/_build/index.html in your browser
```

`docs/index.rst` lists every documented module under the `REST API …` sections.

---

## 🛠️ Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy 2.0** (async) — ORM
- **Alembic** — database migrations
- **PostgreSQL 12** — primary database
- **Redis 7** — caching layer for authenticated users
- **Pydantic Settings** — typed configuration from environment variables
- **python-jose** — JWT encoding/decoding
- **bcrypt** — password hashing
- **slowapi** — rate limiting
- **fastapi-mail** — email sending (registration confirmation & password reset)
- **Cloudinary** — image upload & transformation
- **libgravatar** — Gravatar integration
- **uvicorn** — ASGI server
- **aiosqlite** — in-memory SQLite used by the test suite
- **pytest / pytest-asyncio / pytest-cov / pytest-mock** — testing
- **Sphinx** — API documentation
