# UMT-pythonweb-hw-11

REST API for a contact management application built with **FastAPI**, **SQLAlchemy (async)**, **PostgreSQL**, **JWT authentication**, **Cloudinary** image upload, and **email verification**.

---

## 📋 Requirements

- Python ≥ 3.13
- PostgreSQL 12+ (or Docker)
- Docker / Docker Compose (optional, for running PostgreSQL)

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

Edit `.env` with your actual configuration (database credentials, JWT secret, email SMTP, Cloudinary keys).

### 3. Start PostgreSQL (via Docker)

```bash
docker compose up -d
```

This starts a PostgreSQL 12 container on port `5432` using the credentials from your `.env` file.

> **Note:** If you already have a PostgreSQL instance running, you can skip this step and point `DB_URL` to your existing database.

### 4. Install dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or using **pip**:

```bash
pip install -r requirements.txt
```

> **Note:** If `requirements.txt` is not present, generate it from `pyproject.toml`:
>
> ```bash
> pip install -r <(uv export --format requirements-txt)
> ```
>
> or simply:
>
> ```bash
> uv pip install -e .
> ```

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

## 🗂️ Project Structure

```
├── main.py                  # FastAPI application entry point
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # PostgreSQL container
├── .env.example             # Example environment variables
├── .gitignore
├── pyproject.toml           # Project metadata & dependencies
│
├── migrations/              # Alembic migrations
│   ├── env.py
│   ├── versions/
│   └── ...
│
└── src/
    ├── api/                 # Route handlers (auth, contacts, users, utils)
    ├── conf/                # Configuration (settings, rate limiter)
    ├── database/            # Database session, models
    ├── repository/          # Data access layer
    ├── services/            # Business logic (auth, email, Cloudinary)
    └── schemas.py           # Pydantic schemas
```

---

## 🔑 Environment Variables

| Variable                 | Description                      | Default                  |
| ------------------------ | -------------------------------- | ------------------------ |
| `POSTGRES_DB`            | PostgreSQL database name         | `contacts_db`            |
| `POSTGRES_USER`          | PostgreSQL user                  | `postgres`               |
| `POSTGRES_PASSWORD`      | PostgreSQL password              | _(required)_             |
| `DB_URL`                 | Async database connection string | _(required)_             |
| `JWT_SECRET`             | Secret key for JWT signing       | _(required)_             |
| `JWT_ALGORITHM`          | JWT algorithm                    | `HS256`                  |
| `JWT_EXPIRATION_SECONDS` | Access token TTL (seconds)       | `3600`                   |
| `MAIL_USERNAME`          | SMTP username (email)            | `example@example.com`    |
| `MAIL_PASSWORD`          | SMTP password / app password     | `xxxx xxxx xxxx xxxx`    |
| `MAIL_FROM`              | Sender email address             | `example@example.com`    |
| `MAIL_PORT`              | SMTP port                        | `587`                    |
| `MAIL_SERVER`            | SMTP server                      | `smtp.gmail.com`         |
| `MAIL_FROM_NAME`         | Sender display name              | `Rest API Service`       |
| `MAIL_STARTTLS`          | Enable STARTTLS                  | `True`                   |
| `MAIL_SSL_TLS`           | Enable SSL/TLS                   | `False`                  |
| `USE_CREDENTIALS`        | Use SMTP credentials             | `True`                   |
| `VALIDATE_CERTS`         | Validate SMTP certificates       | `True`                   |
| `CLOUDINARY_NAME`        | Cloudinary cloud name            | _(required for uploads)_ |
| `CLOUDINARY_API_KEY`     | Cloudinary API key               | _(required for uploads)_ |
| `CLOUDINARY_API_SECRET`  | Cloudinary API secret            | _(required for uploads)_ |

See `.env.example` for a complete template.

---

## 🧪 Running Tests

(If tests are added in the future):

```bash
pytest -v
```

---

## 🛠️ Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy 2.0** (async) — ORM
- **Alembic** — database migrations
- **PostgreSQL** — database
- **python-jose** — JWT encoding/decoding
- **bcrypt** — password hashing
- **slowapi** — rate limiting
- **fastapi-mail** — email sending
- **Cloudinary** — image upload & transformation
- **libgravatar** — Gravatar integration
