from app.routers import accounts as accounts_router


def test_create_account(client):
    client.post(
        "/users",
        json={
            "full_name": "Account Customer",
            "email": "account@example.com",
            "password": "AccountPassword@123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={"email": "account@example.com", "password": "AccountPassword@123"},
    )

    token = login_response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.post(
        "/accounts", json={"account_name": "Savings Account", "currency": "INR"}
    )

    assert response.status_code == 201
    assert response.json()["account_name"] == "Savings Account"
    assert response.json()["balance"] == "0.00"


def test_customer_cannot_access_all_users(client):
    client.post(
        "/users",
        json={
            "full_name": "Regular Customer",
            "email": "regular@example.com",
            "password": "CustomerPassword@123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={"email": "regular@example.com", "password": "CustomerPassword@123"},
    )

    token = login_response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users")

    assert response.status_code == 403


def test_admin_can_access_all_users(admin_client):
    response = admin_client.get("/users")

    assert response.status_code == 200


def test_customer_cannot_access_another_customers_account(client):
    # Create first customer
    client.post(
        "/users",
        json={
            "full_name": "Customer One",
            "email": "customer1@example.com",
            "password": "CustomerPassword@123",
        },
    )

    # Login first customer
    login_response = client.post(
        "/auth/login",
        json={"email": "customer1@example.com", "password": "CustomerPassword@123"},
    )

    token_one = login_response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token_one}"})

    # Create first customer's account
    account_response = client.post(
        "/accounts", json={"account_name": "Customer One Savings", "currency": "INR"}
    )

    account_id = account_response.json()["id"]

    # Create second customer
    client.post(
        "/users",
        json={
            "full_name": "Customer Two",
            "email": "customer2@example.com",
            "password": "CustomerPassword@123",
        },
    )

    # Login second customer
    login_response = client.post(
        "/auth/login",
        json={"email": "customer2@example.com", "password": "CustomerPassword@123"},
    )

    token_two = login_response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token_two}"})

    # Attempt to access first customer's account
    response = client.get(f"/accounts/{account_id}")

    assert response.status_code == 404


def test_account_number_collision_retries_successfully(
    customer_client,
    customer_account,
    monkeypatch,
):

    existing_number = customer_account["account_number"]

    generated_numbers = iter(
        [
            existing_number,
            "100199887766",
        ]
    )

    monkeypatch.setattr(
        accounts_router,
        "generate_account_number",
        lambda: next(generated_numbers),
    )

    response = customer_client.post(
        "/accounts",
        json={
            "account_name": "Collision Retry Account",
            "currency": "INR",
        },
    )

    assert response.status_code == 201
    assert response.json()["account_number"] == "100199887766"


def test_account_creation_fails_after_maximum_collision_attempts(
    customer_client,
    customer_account,
    monkeypatch,
):

    existing_number = customer_account["account_number"]

    monkeypatch.setattr(
        accounts_router,
        "generate_account_number",
        lambda: existing_number,
    )

    response = customer_client.post(
        "/accounts",
        json={
            "account_name": "Repeated Collision Account",
            "currency": "INR",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Unable to generate a unique account number. Please try again."
    )
