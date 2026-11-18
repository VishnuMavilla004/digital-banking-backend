
# Digital Banking Backend System

A RESTful digital banking backend built with Python, FastAPI, PostgreSQL, and SQLAlchemy. The project demonstrates secure authentication, account management, financial transactions, transaction history, idempotency, database integrity, and automated testing.

## Project Overview

The Digital Banking Backend provides APIs for customers and administrators to manage banking operations.

## Live Deployment

**Application:** Digital Banking Backend

**Live API:** https://digital-banking-backend-gctw.onrender.com/

**Swagger Documentation:** https://digital-banking-backend-gctw.onrender.com/docs

**Health Check:** https://digital-banking-backend-gctw.onrender.com/health

### Deployment Architecture
- Application hosting: Render
- Containerization: Docker
- Database: Neon PostgreSQL
- Backend framework: FastAPI
- ORM: SQLAlchemy
- Database migrations: Alembic
- Application server: Uvicorn

**Note:** This is an educational portfolio project. Banking transactions are simulated and do not involve real money.

### Core Features

- User registration and authentication
- Password hashing
- JWT-based authentication
- Role-based access control (RBAC)
- Customer account creation and management
- Account ownership validation
- Deposits and withdrawals
- Inter-account transfers
- Transaction history with pagination
- Idempotency protection against duplicate financial operations
- Database transactions and row-level locking
- Centralized exception handling
- Application logging
- Database schema migrations
- Automated API and security testing
- Concurrency testing

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Password Hashing | Argon2 via pwdlib |
| Data Validation | Pydantic |
| Database Migrations | Alembic |
| Testing | Pytest |
| HTTP Testing | FastAPI TestClient / HTTPX |
| Code Quality | Ruff |
| API Documentation | OpenAPI / Swagger UI |

## Architecture

The application follows a layered architecture:

- Routers handle HTTP requests and responses.
- Services contain banking business logic.
- Models define database entities.
- Schemas validate incoming and outgoing data.
- Dependencies provide database sessions and authentication.
- PostgreSQL stores application data.

See [Architecture Documentation](docs/ARCHITECTURE.md).

## Main Banking Capabilities

### Authentication and Authorization

- Register users.
- Authenticate users using email and password.
- Issue JWT access tokens.
- Retrieve the authenticated user's profile.
- Restrict administrative operations to administrators.
- Enforce customer-level resource ownership.

### Account Management

- Create customer accounts.
- Retrieve accounts belonging to the authenticated customer.
- Retrieve and update account information.
- Generate unique account numbers.
- Enforce non-negative account balances.

### Financial Transactions

- Deposit money into an account.
- Withdraw money from an account.
- Transfer money between accounts.
- Retrieve account transaction history.
- Prevent duplicate transaction processing using idempotency keys.

**Note:** Deposits are simulated backend operations. This project does not connect to a real banking network or payment settlement system.

## Reliability and Security

The implementation includes:

- Password hashing rather than plaintext password storage.
- JWT signature and expiry validation.
- Role-based authorization.
- Account ownership checks.
- SQLAlchemy transaction management.
- PostgreSQL row-level locking for financial operations.
- Deterministic locking order for transfers.
- Idempotency key validation.
- Database-level integrity constraints.
- Centralized exception handling.
- Logging without intentionally recording authentication credentials.
- Separate application and test databases.

This is an educational portfolio project, not a certified production banking platform.

## Project Structure

```text
app/
    main.py
    database.py
    dependencies.py
    security.py
    auth_dependencies.py
    logging_config.py
    exception_handlers.py

    models/
        user.py
        account.py
        transaction.py

    schemas/
        user.py
        account.py
        auth.py
        transaction.py

    routers/
        users.py
        auth.py
        accounts.py

    services/
        banking.py

tests/
    conftest.py
    test_app.py
    test_users.py
    test_auth.py
    test_accounts.py
    test_transactions.py
    test_security.py
    test_validation.py
    test_admin.py
    test_workflows.py
    test_exception_handlers.py
    test_concurrency.py
    test_database_constraints.py
    test_jwt_config.py

migrations/
docs/
scripts/
```
## Common Response Codes

| Code | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created successfully |
| 204 | Resource deleted successfully (no response body) |
| 400 | Bad request |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation error |
| 500 | Internal server error |

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/VishnuMavilla004/digital-banking-backend.git
cd digital-banking-backend
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`.

Update the database credentials and JWT configuration locally.

Never commit `.env` or expose its contents.

### 5. Create PostgreSQL databases

Create two separate databases:

- `digital_banking` — application database
- `digital_banking_test` — automated test database

The test database must never be replaced with the development database.

### 6. Apply migrations

```powershell
alembic upgrade head
```

### 7. Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

## API Documentation

The complete API reference is available in:

- [API Reference](docs/API_REFERENCE.md)
- [OpenAPI Specification](docs/openapi.json)
- Swagger UI at `/docs`

## Running Tests

Run the complete test suite:

```powershell
pytest -v
```

Run code-quality checks:

```powershell
ruff check app tests
ruff format --check app tests
python -m compileall app tests migrations
```

Check database migrations:

```powershell
alembic current
alembic check
```

The project has passed a 111-test checkpoint covering API behavior, authentication, authorization, banking workflows, database constraints, and concurrent operations.

Always run the latest test suite against the isolated test database before publishing changes.

## Database Design

The system uses three principal entities:

- Users
- Accounts
- Transactions

A user can own multiple accounts. Transactions reference source and destination accounts.

See [Database ER Diagram](docs/ARCHITECTURE.md).

## Future Improvements

Potential extensions include:

- Refresh token rotation and revocation
- Account statement exports
- Transaction notifications
- Rate limiting
- Audit trails
- Docker-based development
- CI/CD with GitHub Actions
- Deployment with managed PostgreSQL
- Integration with a payment sandbox

## Author

Python Backend Development Portfolio Project

**Focus:** Backend Engineering | REST APIs | Python | FastAPI | PostgreSQL | SQLAlchemy | Authentication | Automated Testing
