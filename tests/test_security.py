def test_account_access_without_token(client):
    response = client.get("/accounts")

    assert response.status_code == 401


def test_account_access_with_invalid_token(client):
    response = client.get(
        "/accounts", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_account_access_with_malformed_token(client):
    response = client.get("/accounts", headers={"Authorization": "Bearer abc.def"})

    assert response.status_code == 401


def test_customer_cannot_access_all_users(customer_client):
    response = customer_client.get("/users")

    assert response.status_code == 403


def test_customer_cannot_access_another_user(customer_client):
    register_response = customer_client.post(
        "/users",
        json={
            "full_name": "Second Customer",
            "email": "security.second@example.com",
            "password": "SecondPassword@123",
        },
    )

    assert register_response.status_code == 201

    second_user_id = register_response.json()["id"]

    response = customer_client.get(f"/users/{second_user_id}")

    assert response.status_code == 403


def test_customer_cannot_delete_another_user(customer_client):
    register_response = customer_client.post(
        "/users",
        json={
            "full_name": "Delete Protection Customer",
            "email": "security.delete@example.com",
            "password": "DeletePassword@123",
        },
    )

    assert register_response.status_code == 201

    other_user_id = register_response.json()["id"]

    response = customer_client.delete(f"/users/{other_user_id}")

    assert response.status_code == 403


def test_customer_cannot_modify_another_user(customer_client):
    register_response = customer_client.post(
        "/users",
        json={
            "full_name": "Protected Customer",
            "email": "security.patch@example.com",
            "password": "ProtectedPassword@123",
        },
    )

    assert register_response.status_code == 201

    other_user_id = register_response.json()["id"]

    response = customer_client.patch(
        f"/users/{other_user_id}", json={"full_name": "Unauthorized Modification"}
    )

    assert response.status_code == 403


def test_customer_can_access_own_profile(customer_client):
    response = customer_client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "customer.test@example.com"


def test_customer_can_access_own_account(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.get(f"/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["id"] == account_id


def test_customer_cannot_access_another_customers_account(
    customer_client, customer_account
):
    first_account_id = customer_account["id"]

    register_response = customer_client.post(
        "/users",
        json={
            "full_name": "Another Account Owner",
            "email": "security.owner@example.com",
            "password": "OwnerPassword@123",
        },
    )

    assert register_response.status_code == 201

    login_response = customer_client.post(
        "/auth/login",
        json={"email": "security.owner@example.com", "password": "OwnerPassword@123"},
    )

    assert login_response.status_code == 200

    second_token = login_response.json()["access_token"]

    response = customer_client.get(
        f"/accounts/{first_account_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert response.status_code == 404


def test_customer_cannot_escalate_own_role(customer_client):
    profile_response = customer_client.get("/auth/me")

    assert profile_response.status_code == 200

    user_id = profile_response.json()["id"]

    response = customer_client.patch(
        f"/users/{user_id}",
        json={
            "role": "admin",
            "full_name": "Updated Customer",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "customer"

    refreshed_profile = customer_client.get("/auth/me")

    assert refreshed_profile.status_code == 200
    assert refreshed_profile.json()["role"] == "customer"
