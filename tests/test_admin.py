def test_admin_can_retrieve_all_users(admin_client):
    response = admin_client.get("/users")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_can_retrieve_another_user(admin_client):
    register_response = admin_client.post(
        "/users",
        json={
            "full_name": "Admin Test Customer",
            "email": "admin.customer@example.com",
            "password": "CustomerPassword@123",
        },
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    response = admin_client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_admin_can_delete_user(admin_client):
    register_response = admin_client.post(
        "/users",
        json={
            "full_name": "User To Delete",
            "email": "delete.target@example.com",
            "password": "DeletePassword@123",
        },
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    response = admin_client.delete(f"/users/{user_id}")

    assert response.status_code == 204

    verification_response = admin_client.get(f"/users/{user_id}")

    assert verification_response.status_code == 404


def test_unauthenticated_user_cannot_retrieve_all_users(client):
    response = client.get("/users")

    assert response.status_code == 401


def test_customer_cannot_delete_another_user(customer_client):
    register_response = customer_client.post(
        "/users",
        json={
            "full_name": "Protected User",
            "email": "admin.protected@example.com",
            "password": "ProtectedPassword@123",
        },
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    response = customer_client.delete(f"/users/{user_id}")

    assert response.status_code == 403


def test_admin_gets_404_for_nonexistent_user(admin_client):
    response = admin_client.get("/users/999999999")

    assert response.status_code == 404


def test_admin_can_update_another_user(admin_client):
    register_response = admin_client.post(
        "/users",
        json={
            "full_name": "Original Customer",
            "email": "original.customer@example.com",
            "password": "CustomerPassword@123",
        },
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    response = admin_client.patch(
        f"/users/{user_id}", json={"full_name": "Updated Customer"}
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Customer"


def test_account_creation_ignores_another_users_id(customer_client):
    register_response = customer_client.post(
        "/users",
        json={
            "full_name": "Other Account Owner",
            "email": "spoof.target@example.com",
            "password": "TargetPassword@123",
        },
    )

    assert register_response.status_code == 201

    other_user_id = register_response.json()["id"]

    response = customer_client.post(
        "/accounts",
        json={
            "account_name": "Ownership Test Account",
            "currency": "INR",
            "user_id": other_user_id,
        },
    )

    assert response.status_code == 201

    assert response.json()["user_id"] != other_user_id
