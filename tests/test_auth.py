def test_login_success(client):
    client.post(
        "/users",
        json={
            "full_name": "Login Customer",
            "email": "login@example.com",
            "password": "LoginPassword@123",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "LoginPassword@123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"].lower() == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/users",
        json={
            "full_name": "Login Customer",
            "email": "wrongpass@example.com",
            "password": "CorrectPassword@123",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "WrongPassword@123"},
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "SomePassword@123"},
    )

    assert response.status_code == 401
