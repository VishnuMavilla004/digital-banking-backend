def create_second_account(customer_client):
    response = customer_client.post(
        "/accounts", json={"account_name": "Second Savings Account", "currency": "INR"}
    )

    assert response.status_code == 201

    return response.json()


def test_registration_rejects_missing_email(client):
    response = client.post(
        "/users", json={"full_name": "Validation User", "password": "Password@123"}
    )

    assert response.status_code == 422


def test_registration_rejects_invalid_email(client):
    response = client.post(
        "/users",
        json={
            "full_name": "Validation User",
            "email": "invalid-email",
            "password": "Password@123",
        },
    )

    assert response.status_code == 422


def test_registration_rejects_missing_password(client):
    response = client.post(
        "/users",
        json={"full_name": "Validation User", "email": "validation@example.com"},
    )

    assert response.status_code == 422


def test_deposit_rejects_negative_amount(customer_client, customer_account):
    response = customer_client.post(
        f"/accounts/{customer_account['id']}/deposit",
        headers={"Idempotency-Key": "validation-deposit-001"},
        json={"amount": "-100.00"},
    )

    assert response.status_code == 422


def test_deposit_rejects_excess_decimal_places(customer_client, customer_account):
    response = customer_client.post(
        f"/accounts/{customer_account['id']}/deposit",
        headers={"Idempotency-Key": "validation-deposit-002"},
        json={"amount": "100.123"},
    )

    assert response.status_code == 422


def test_withdrawal_rejects_negative_amount(customer_client, customer_account):
    response = customer_client.post(
        f"/accounts/{customer_account['id']}/withdraw",
        headers={"Idempotency-Key": "validation-withdraw-001"},
        json={"amount": "-100.00"},
    )

    assert response.status_code == 422


def test_transfer_rejects_zero_amount(customer_client, customer_account):
    destination = create_second_account(customer_client)

    response = customer_client.post(
        f"/accounts/{customer_account['id']}/transfer",
        headers={"Idempotency-Key": "validation-transfer-001"},
        json={"destination_account_id": destination["id"], "amount": "0.00"},
    )

    assert response.status_code == 422


def test_transfer_rejects_invalid_destination_id(customer_client, customer_account):
    response = customer_client.post(
        f"/accounts/{customer_account['id']}/transfer",
        headers={"Idempotency-Key": "validation-transfer-002"},
        json={"destination_account_id": -1, "amount": "100.00"},
    )

    assert response.status_code == 422


def test_account_creation_rejects_missing_account_name(customer_client):
    response = customer_client.post("/accounts", json={"currency": "INR"})

    assert response.status_code == 422


def test_account_creation_rejects_invalid_currency(customer_client):
    response = customer_client.post(
        "/accounts",
        json={"account_name": "Invalid Currency Account", "currency": "INRR"},
    )

    assert response.status_code == 422


def test_transaction_history_rejects_invalid_limit(customer_client, customer_account):
    response = customer_client.get(
        f"/accounts/{customer_account['id']}/transactions",
        params={"skip": 0, "limit": 0},
    )

    assert response.status_code == 422


def test_transaction_history_returns_404_for_nonexistent_account(customer_client):
    response = customer_client.get("/accounts/999999999/transactions")

    assert response.status_code == 404
