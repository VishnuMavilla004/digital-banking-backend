
# System Architecture

## 1. Application Architecture

```mermaid
flowchart TD
    Client[API Client / Swagger UI]

    Client --> Router[FastAPI Routers]

    Router --> Auth[Authentication Dependencies]
    Router --> Schema[Pydantic Schemas]
    Router --> Service[Banking Service Layer]

    Auth --> Security[JWT and Password Security]
    Service --> ORM[SQLAlchemy ORM]
    ORM --> DB[(PostgreSQL)]

    Router --> Exception[Exception Handlers]
    Service --> Logging[Application Logging]

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
| Tests | Functional, security and concurrency verification |

## 3. Database ER Diagram

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

## 4. Transfer Processing Flow

```mermaid
flowchart TD
    A[Receive Transfer Request] --> B[Validate Request]
    B --> C[Check Idempotency Key]
    C --> D[Lock Source and Destination Accounts]
    D --> E{Source Account Owned by User?}
    E -->|No| F[Return Error]
    E -->|Yes| G{Destination Exists?}
    G -->|No| F
    G -->|Yes| H{Currency Matches?}
    H -->|No| F
    H -->|Yes| I{Sufficient Balance?}
    I -->|No| F
    I -->|Yes| J[Debit Source]
    J --> K[Credit Destination]
    K --> L[Create Transaction Record]
    L --> M[Commit Database Transaction]
    M --> N[Return Transaction]
```

## 5. Transaction Reliability

```
The banking service uses:

- Database transactions to group related updates.
- Row-level locking to protect account balances.
- Consistent lock ordering during transfers.
- Idempotency keys to prevent duplicate operations.
- Database constraints to protect stored data.

The project is an educational implementation. External banking integrations, payment settlement, regulatory controls, and production operational safeguards are outside its current scope.
```

Rather than manually guessing endpoint paths, we'll generate documentation directly from FastAPI's OpenAPI schema. This ensures the published API reference matches your actual routers.