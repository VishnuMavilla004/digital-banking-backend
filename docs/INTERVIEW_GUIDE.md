
# Digital Banking Backend — Interview Guide

## 1. Project Overview

This project is a RESTful digital banking backend built using Python, FastAPI, PostgreSQL, and SQLAlchemy.

It supports user authentication, role-based authorization, account management, deposits, withdrawals, transfers, and transaction history.

The main engineering focus is data integrity, authentication, idempotency, concurrency control, and automated testing.

## 2. Why Did You Choose FastAPI?

FastAPI provides:

- Automatic OpenAPI documentation.
- Request validation using Pydantic.
- Dependency injection.
- Asynchronous endpoint support.
- Integration with SQLAlchemy and Python type hints.

It makes API development structured and efficient.

## 3. Explain JWT Authentication

JWT is a token-based authentication mechanism.

The login process:

1. User submits email and password.
2. Backend retrieves the user.
3. Password is verified against the stored Argon2 hash.
4. Backend generates a signed JWT.
5. Client sends the token in subsequent requests.
6. Authentication dependency validates the token.
7. Backend identifies the authenticated user.

Passwords are never stored as plaintext.

## 4. What Is RBAC?

Role-Based Access Control restricts operations according to a user's role.

For example:

- Customers can access their own banking resources.
- Administrators can access authorized administrative operations.

Role authorization and resource ownership checks solve different problems. Both are required.

## 5. Why Use Decimal Instead of Float?

Floating-point numbers cannot represent every decimal fraction exactly.

Financial calculations require predictable decimal precision.

Python's Decimal type is appropriate for monetary values because it avoids common binary floating-point precision errors.

## 6. What Is Idempotency?

Idempotency means repeating the same request does not create another financial operation.

For example:

A client sends a deposit request with an idempotency key.

If the client retries because it did not receive the response, the backend checks the existing key and returns the previous result rather than processing the deposit again.

This helps prevent duplicate financial operations.

## 7. What Is a Database Transaction?

A database transaction groups multiple database operations into one logical unit.

A transfer involves:

1. Deducting money from the sender.
2. Adding money to the receiver.
3. Recording the transaction.

These changes must succeed or fail together.

This is the purpose of transaction commit and rollback behavior.

## 8. Why Use SELECT FOR UPDATE?

Concurrent requests can attempt to modify the same account balance.

Row-level locking prevents another transaction from modifying the locked account row until the current transaction finishes.

This protects balance calculations from conflicting concurrent updates.

## 9. Why Use Consistent Lock Ordering?

Two concurrent transfers could otherwise lock the same accounts in opposite orders.

For example:

- Transaction A locks Account 1 and waits for Account 2.
- Transaction B locks Account 2 and waits for Account 1.

This can produce a deadlock.

Locking account rows in a consistent order reduces this risk.

## 10. Why Use PostgreSQL Constraints?

Application validation alone is not enough to protect stored data.

Database constraints provide another layer of protection.

Examples include:

- Unique account numbers.
- Unique idempotency keys.
- Non-negative balances.
- Valid transaction amounts.
- Valid transaction states.

## 11. Why Use Alembic?

Alembic manages database schema changes over time.

It provides versioned migrations so the database structure can evolve without manually recreating the database.

Typical commands:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic current
alembic check
```

## 12. How Did You Test the Application?

The project uses Pytest and HTTPX.

Testing covers:

- Authentication.
- Authorization.
- API validation.
- Account ownership.
- Banking workflows.
- Idempotency.
- Database constraints.
- Exception handling.
- Concurrent transactions.

The test database is isolated from the application database.

## 13. How Is the Project Deployed?

The application is containerized using Docker.

Docker Compose provides local application and PostgreSQL services.

The hosted application runs on Render and uses Neon PostgreSQL.

Alembic applies database migrations during container startup.

GitHub Actions runs automated quality checks and tests.

## 14. What Are the Current Limitations?

The project is a portfolio implementation.

It does not integrate with real banking networks or payment settlement systems.

It does not claim production banking certification or regulatory compliance.

Further work could include refresh-token rotation, audit trails, rate limiting, monitoring, and payment-provider sandbox integration.

## 15. Explain Your Most Important Engineering Decision

A strong example is the transfer operation.

A transfer must preserve consistency across two account balances and a transaction record.

I used database transactions, row-level locking, consistent lock ordering, idempotency checks, and database constraints to make the operation more reliable under concurrent requests and client retries.
