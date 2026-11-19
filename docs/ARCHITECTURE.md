
# System Architecture

# API Reference

Interactive documentation:
https://digital-banking-backend-gctw.onrender.com/docs

Live API:
https://digital-banking-backend-gctw.onrender.com

Health check:
https://digital-banking-backend-gctw.onrender.com/health

The OpenAPI specification is available at `/openapi.json`.

## 1. Application Overview

The Digital Banking Backend follows a layered architecture built with FastAPI, SQLAlchemy, and PostgreSQL.

```mermaid
flowchart TD
    Client[API Client / Swagger UI]

    Client --> Router[FastAPI Routers]

    Router --> Schema[Pydantic Schemas]
    Router --> Auth[Authentication Dependencies]
    Router --> Service[Banking Service Layer]

    Auth --> Security[JWT and Argon2 Security]
    Service --> ORM[SQLAlchemy ORM]

    ORM --> DB[(PostgreSQL)]

    Migration[Alembic Migrations] --> DB

    Tests[Pytest Test Suite] --> Router
    Tests --> Service
    Tests --> DB
```

## 2. Layer Responsibilities

| Layer | Responsibility |
|---|---|
| Routers | HTTP endpoints and request handling |
| Schemas | Request validation and response serialization |
| Services | Banking business logic |
| Models | SQLAlchemy database entities |
| Dependencies | Database sessions and authentication |
| Security | Password hashing and JWT handling |
| Exception Handlers | Consistent API error responses |
| Migrations | Database schema versioning |
| Tests | Functional, security, and concurrency verification |

## 3. Database Design

The system uses three principal entities:

- Users
- Accounts
- Transactions

```mermaid
erDiagram
    USERS ||--o{ ACCOUNTS : owns
    ACCOUNTS ||--o{ TRANSACTIONS : source
    ACCOUNTS ||--o{ TRANSACTIONS : destination

    USERS {
        int id PK
        string full_name
        string email UK
        string password_hash
        string role
        datetime created_at
    }

    ACCOUNTS {
        int id PK
        string account_number UK
        int user_id FK
        string account_name
        decimal balance
        string currency
        datetime created_at
    }

    TRANSACTIONS {
        int id PK
        int source_account_id FK
        int destination_account_id FK
        decimal amount
        string transaction_type
        string status
        datetime created_at
        string idempotency_key UK
    }
```

A user can own multiple accounts.

Transactions reference the relevant source and destination accounts according to the transaction type.

## 4. Transfer Processing

A transfer must debit one account and credit another without allowing inconsistent intermediate results.

```mermaid
flowchart TD
    A[Receive Transfer Request]
    B[Validate Request]
    C[Check Idempotency Key]
    D[Lock Accounts in Consistent Order]
    E{Source Account Owned by User?}
    F{Destination Exists?}
    G{Currency Matches?}
    H{Sufficient Balance?}
    I[Debit Source]
    J[Credit Destination]
    K[Create Transaction Record]
    L[Commit Database Transaction]
    M[Return Transaction]
    X[Return Error]

    A --> B --> C --> D --> E
    E -- No --> X
    E -- Yes --> F
    F -- No --> X
    F -- Yes --> G
    G -- No --> X
    G -- Yes --> H
    H -- No --> X
    H -- Yes --> I --> J --> K --> L --> M
```

## 5. Transaction Reliability

The banking service uses:

- Database transactions to group related updates.
- PostgreSQL row-level locking to protect account balances.
- Consistent account-lock ordering during transfers.
- Idempotency keys to prevent duplicate operations.
- Database constraints to protect stored data.
- Decimal-based monetary values to avoid floating-point arithmetic errors.

## 6. Authentication and Authorization

Authentication uses:

- Argon2 password hashing.
- JWT access tokens.
- Token signature validation.
- Token expiration validation.
- Authenticated-user dependencies.
- Role-based administrative authorization.
- Account ownership checks.

## 7. Testing Architecture

The project uses Pytest and HTTPX.

The test suite covers:

- User registration and authentication.
- Authorization and ownership restrictions.
- Account creation and management.
- Deposits, withdrawals, and transfers.
- Idempotency behavior.
- Database constraints.
- Exception handling.
- Concurrent transaction behavior.

The application and test environments use separate databases.

## 8. Deployment Architecture

```mermaid
flowchart TD
    User[API Client]
    Render[Render Web Service]
    Docker[Docker Container]
    FastAPI[FastAPI Application]
    Neon[(Neon PostgreSQL)]

    User --> Render
    Render --> Docker
    Docker --> FastAPI
    FastAPI --> Neon
```

Docker packages the application.

Render hosts the API.

Neon provides hosted PostgreSQL.

Alembic manages database migrations.

## 9. Scope and Limitations

This is an educational backend implementation.

It does not provide real payment settlement, external banking network connectivity, regulatory compliance certification, or production-grade financial infrastructure.

| `GET` | `/health` | Database connectivity health check | Health |