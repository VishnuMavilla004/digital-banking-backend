
# Digital Banking Backend System

A RESTful banking backend built using Python, FastAPI, PostgreSQL, and SQLAlchemy. The application demonstrates secure authentication, account management, financial transactions, transaction integrity, idempotency, concurrency control, automated testing, and cloud deployment.

## Live Application

| Resource | URL |
|---|---|
| API Base URL | https://digital-banking-backend-gctw.onrender.com |
| Swagger UI | https://digital-banking-backend-gctw.onrender.com/docs |
| Health Check | https://digital-banking-backend-gctw.onrender.com/health |

The health endpoint verifies application and database connectivity.

> The hosted service uses free-tier infrastructure. Initial requests after inactivity may take longer because the service can sleep.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11 |
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Validation | Pydantic |
| Database Migrations | Alembic |
| Testing | Pytest, HTTPX |
| Code Quality | Ruff |
| Containerization | Docker |
| Local Orchestration | Docker Compose |
| Application Hosting | Render |
| Hosted Database | Neon PostgreSQL |
| API Documentation | OpenAPI, Swagger UI |
| CI | GitHub Actions |

## Core Features

### Authentication and Authorization
- User registration and login
- Argon2 password hashing
- JWT access-token authentication
- Role-based access control
- Customer resource ownership validation
- Protected administrative operations

### Account Management
- Customer account creation
- Account retrieval and updates
- Unique account number generation
- Account ownership enforcement
- Non-negative balance validation

### Banking Transactions
- Deposits
- Withdrawals
- Account-to-account transfers
- Transaction history with pagination
- Idempotency-key protection
- Database transaction management
- PostgreSQL row-level locking
- Deterministic locking order during transfers

### Reliability and Quality
- Database-level integrity constraints
- Centralized exception handling
- Application logging
- Separate application and test databases
- Automated API and security tests
- Concurrency tests
- Alembic migration management
- Docker-based deployment
- GitHub Actions CI workflow

## Architecture

The application follows a layered backend architecture:

- Routers handle HTTP requests.
- Schemas validate requests and serialize responses.
- Services implement banking business logic.
- Models define database entities.
- Dependencies manage database sessions and authentication.
- PostgreSQL stores application data.
- Alembic manages database schema changes.

See [Architecture Documentation](docs/ARCHITECTURE.md).

## Transaction Reliability

Financial operations require special handling to protect account balances.

The transfer implementation uses:

1. Request validation.
2. Idempotency-key verification.
3. Database transaction management.
4. Row-level locks on the relevant accounts.
5. Consistent account-lock ordering.
6. Balance validation.
7. Debit and credit operations.
8. Transaction record creation.
9. Database commit.

These mechanisms help prevent duplicate processing and conflicting concurrent balance updates.

See [Architecture Documentation](docs/ARCHITECTURE.md).

## Project Structure

```text
digital-banking-backend/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   ├── security.py
│   ├── auth_dependencies.py
│   ├── exception_handlers.py
│   └── logging_config.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   ├── INTERVIEW_GUIDE.md
│   └── openapi.json
│
├── migrations/
├── scripts/
├── tests/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

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

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Update the local PostgreSQL credentials and JWT configuration in `.env`.

### 5. Create PostgreSQL databases

Create these two separate databases:

- `digital_banking`
- `digital_banking_test`

Never use the application database as the automated test database.

### 6. Apply migrations

```bash
alembic upgrade head
```

### 7. Start the application

```bash
python -m uvicorn app.main:app --reload
```

Application:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

## Docker Setup

Requirements: Docker Desktop and Docker Compose.

Start the application:

```bash
docker compose up --build -d
```

Inspect containers:

```bash
docker compose ps
```

Inspect API logs:

```bash
docker compose logs api
```

Stop containers:

```bash
docker compose down
```

The Docker Compose database uses a persistent named volume.

## Testing

Run the complete automated test suite:

```bash
pytest -v
```

Run code-quality checks:

```bash
ruff check app tests scripts
ruff format --check app tests scripts
```

Compile the application:

```bash
python -m compileall app tests migrations scripts
```

Verify database migrations:

```bash
alembic current
alembic check
```

The project previously passed a 111-test checkpoint covering authentication, authorization, API workflows, database constraints, exception handling, and concurrent transactions. Run the current test suite for the latest result.

## Continuous Integration

GitHub Actions automatically runs:

- Ruff lint checks
- Formatting verification
- Python compilation
- Alembic migration checks
- Automated tests
- Docker image build

Workflow configuration:

`.github/workflows/ci.yml`

## Documentation

- [System Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Interview Preparation Guide](docs/INTERVIEW_GUIDE.md)
- [OpenAPI Specification](docs/openapi.json)

## Important Project Scope

This is an educational backend engineering portfolio project.

Deposits and withdrawals are simulated application operations. The system does not connect to a real banking network, payment gateway, or settlement infrastructure.

It is not a certified production banking platform.

## Author

Python Backend Development Portfolio Project

Focus: Backend Engineering | Python | FastAPI | PostgreSQL | SQLAlchemy | REST APIs | Authentication | Database Transactions | Automated Testing
