import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

import app.models
from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models import User
from app.security import hash_password

load_dotenv()


@pytest.fixture(scope="session")
def test_engine():
    test_database_name = os.getenv("DB_TEST_NAME")

    if test_database_name != "digital_banking_test":
        raise RuntimeError("Tests must use the digital_banking_test database.")

    test_database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=test_database_name,
    )

    engine = create_engine(test_database_url, echo=False)

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    outer_transaction = connection.begin()

    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_admin(db_session):
    admin = User(
        full_name="Test Administrator",
        email="test.admin@example.com",
        password_hash=hash_password("AdminPassword@123"),
        role="admin",
    )

    db_session.add(admin)
    db_session.flush()

    return admin


@pytest.fixture
def admin_client(client, test_admin):
    response = client.post(
        "/auth/login",
        json={"email": "test.admin@example.com", "password": "AdminPassword@123"},
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


@pytest.fixture
def customer_client(client):
    response = client.post(
        "/users",
        json={
            "full_name": "Test Customer",
            "email": "customer.test@example.com",
            "password": "CustomerPassword@123",
        },
    )

    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "customer.test@example.com", "password": "CustomerPassword@123"},
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


@pytest.fixture
def customer_account(customer_client):
    response = customer_client.post(
        "/accounts", json={"account_name": "Test Savings Account", "currency": "INR"}
    )

    assert response.status_code == 201

    return response.json()
