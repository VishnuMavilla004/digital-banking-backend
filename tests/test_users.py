def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "full_name": "Test Customer",
            "email": "test.customer@example.com",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test Customer"
    assert data["email"] == "test.customer@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_user(client):
    response = client.post(
        "/users",
        json={
            "full_name": "Test Customer",
            "email": "test.customer@example.com",
            "password": "TestPassword@123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test Customer"
    assert data["email"] == "test.customer@example.com"
    assert data["role"] == "customer"

    # Password must never appear in the response
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    user_data = {
        "full_name": "Test Customer",
        "email": "duplicate@example.com",
        "password": "TestPassword@123",
    }

    first_response = client.post("/users", json=user_data)

    second_response = client.post("/users", json=user_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_register_invalid_email(client):
    response = client.post(
        "/users",
        json={
            "full_name": "Invalid Customer",
            "email": "invalid-email",
            "password": "TestPassword@123",
        },
    )

    assert response.status_code == 422


def test_user_not_found(admin_client):
    response = admin_client.get("/users/999999")

    assert response.status_code == 404
