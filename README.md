# FastAPI Auth Service

Production-ready auth service using **Python 3.12**, **FastAPI**, **PostgreSQL**, and **Docker**.

## Features
- User registration & login
- JWT access & refresh tokens (rotating refresh tokens)
- Secure password hashing (bcrypt via passlib)
- Logout (refresh token invalidation)
- Token refresh
- `GET /me` (current user)
- Change password
- Optional email verification hooks (stubbed)
- SQLAlchemy 2.0 + Alembic migrations
- Pydantic Settings for configuration
- Docker Compose with PostgreSQL
- Pytest tests for the critical happy-path
- Makefile helpers & pre-commit config

## Quickstart

```bash
cp .env.example .env
# (edit the .env secrets if needed)

docker compose up --build
# API will be on http://127.0.0.1:8000
```

Then open docs: http://localhost:8000/docs

### Run migrations (inside the `app` container)

```bash
docker compose exec api alembic upgrade head
```

### Run tests (inside the `app` container)
```bash
docker compose exec api pytest -q
```

## Endpoints (summary)
- `POST /auth/register` – create account
- `POST /auth/login` – obtain access & refresh tokens
- `POST /auth/refresh` – rotate refresh & issue new pair
- `POST /auth/logout` – invalidate refresh token
- `GET /auth/me` – current user
- `POST /auth/change-password` – change password
- `DELETE /auth/delete-account - delete account
- (stubs) `POST /auth/request-reset`, `POST /auth/reset-password`, `POST /auth/verify-email`

See complete OpenAPI at `/docs`.

## Project layout
```
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  security.py
  deps.py
  routers/
    auth.py
alembic/
  env.py
  script.py.mako
  versions/
tests/
  conftest.py
  test_auth_all.py
Dockerfile
docker-compose.yml
alembic.ini
requirements.txt
Makefile
.env.example
.gitignore
REAMDE.md
pytest.ini
```

## Notes
- Refresh tokens are stored & rotated in DB (`user_tokens` table). Old tokens are invalid after refresh/logout.
- Access tokens are short-lived (default 15min).
- Both tokens are returned in JSON; you can also adapt to httponly cookies easily.
- Email flows are stubbed; wire them to your provider (e.g., Yandex).
```

Developer:
* [Dauletnazar Mambetnazarov.](https://github.com/Dauletnazarr/)
