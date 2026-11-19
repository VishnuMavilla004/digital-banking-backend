
# Deployment Guide

## Deployment Architecture

- Application: FastAPI
- Containerization: Docker
- Application hosting: Render
- Database hosting: Neon PostgreSQL
- Database migrations: Alembic
- Application server: Uvicorn

## Live Endpoints

- API: https://digital-banking-backend-gctw.onrender.com
- Swagger: https://digital-banking-backend-gctw.onrender.com/docs
- Health: https://digital-banking-backend-gctw.onrender.com/health

## Local Docker Deployment

Requirements:

- Docker Desktop
- Docker Compose
- Configured environment variables

Start:

```bash
docker compose up --build -d
```

Check:

```bash
docker compose ps
docker compose logs api
```

Stop:

```bash
docker compose down
```

## Hosted Environment Variables

The hosted application requires:

- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
- DB_NAME
- JWT_SECRET_KEY
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES

Configure secrets through the hosting provider's environment settings.

Never commit production credentials to GitHub.

## Database Migrations

Alembic applies pending migrations during container startup.

```bash
alembic upgrade head
```

## Health Verification

The application exposes:

- `/` — application status
- `/health` — database connectivity
- `/docs` — Swagger UI
- `/openapi.json` — OpenAPI specification

## Deployment Limitations

The hosted free-tier configuration is intended for educational demonstration.

Compute resources can sleep, database usage is limited, and availability is not guaranteed.

This is not a production banking deployment.
