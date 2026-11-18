from decimal import Decimal


def test_complete_banking_workflow(customer_client, customer_account):
    """
    Deposit -> Withdraw -> Transfer -> Verify balances and history.
    """

    source_id = customer_account["id"]

    # Create a second account belonging to the same customer.
    response = customer_client.post(
        "/accounts", json={"account_name": "Secondary Savings", "currency": "INR"}
    )

    assert response.status_code == 201
    destination_id = response.json()["id"]

    # Deposit ₹1,000 into the source account.
    response = customer_client.post(
        f"/accounts/{source_id}/deposit",
        json={"amount": "1000.00"},
        headers={"Idempotency-Key": "workflow-deposit-001"},
    )
    assert response.status_code == 201

    # Withdraw ₹100 from the source account.
    response = customer_client.post(
        f"/accounts/{source_id}/withdraw",
        json={"amount": "100.00"},
        headers={"Idempotency-Key": "workflow-withdraw-001"},
    )
    assert response.status_code == 201

    # Transfer ₹300 from the source to the destination.
    response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        json={"destination_account_id": destination_id, "amount": "300.00"},
        headers={"Idempotency-Key": "workflow-transfer-001"},
    )
    assert response.status_code == 201

    # Verify source account balance: 1000 - 100 - 300 = 600.
    response = customer_client.get(f"/accounts/{source_id}")
    assert response.status_code == 200
    assert Decimal(str(response.json()["balance"])) == Decimal("600.00")

    # Verify destination account balance: 300.
    response = customer_client.get(f"/accounts/{destination_id}")
    assert response.status_code == 200
    assert Decimal(str(response.json()["balance"])) == Decimal("300.00")

    # Verify transaction histories.
    source_history = customer_client.get(f"/accounts/{source_id}/transactions")
    destination_history = customer_client.get(
        f"/accounts/{destination_id}/transactions"
    )

    assert source_history.status_code == 200
    assert destination_history.status_code == 200

    assert len(source_history.json()) == 3
    assert len(destination_history.json()) == 1


def test_registration_login_and_authenticated_profile(client):
    # Register a new customer.
    response = client.post(
        "/users",
        json={
            "full_name": "Workflow Customer",
            "email": "workflow.customer@example.com",
            "password": "WorkflowPassword@123",
        },
    )

    assert response.status_code == 201

    # Log in with the registered credentials.
    response = client.post(
        "/auth/login",
        json={
            "email": "workflow.customer@example.com",
            "password": "WorkflowPassword@123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    # Access the authenticated user's profile.
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "workflow.customer@example.com"


def test_insufficient_funds_do_not_change_balances(customer_client, customer_account):
    source_id = customer_account["id"]

    # Deposit ₹100.
    response = customer_client.post(
        f"/accounts/{source_id}/deposit",
        json={"amount": "100.00"},
        headers={"Idempotency-Key": "workflow-small-deposit-001"},
    )
    assert response.status_code == 201

    # Attempt to withdraw ₹150.
    response = customer_client.post(
        f"/accounts/{source_id}/withdraw",
        json={"amount": "150.00"},
        headers={"Idempotency-Key": "workflow-large-withdraw-001"},
    )

    assert response.status_code == 400

    # Balance must remain unchanged after the rejected withdrawal.
    response = customer_client.get(f"/accounts/{source_id}")

    assert response.status_code == 200
    assert Decimal(str(response.json()["balance"])) == Decimal("100.00")


def test_replayed_deposit_does_not_duplicate_money(customer_client, customer_account):
    account_id = customer_account["id"]
    headers = {"Idempotency-Key": "workflow-replay-deposit-001"}
    payload = {"amount": "500.00"}

    # First deposit.
    first_response = customer_client.post(
        f"/accounts/{account_id}/deposit", json=payload, headers=headers
    )
    assert first_response.status_code == 201

    # Replay the same request with the same key.
    second_response = customer_client.post(
        f"/accounts/{account_id}/deposit", json=payload, headers=headers
    )
    assert second_response.status_code == 201

    # Both responses should refer to the same transaction.
    assert first_response.json()["id"] == second_response.json()["id"]

    # The balance must increase only once.
    account_response = customer_client.get(f"/accounts/{account_id}")

    assert account_response.status_code == 200
    assert Decimal(str(account_response.json()["balance"])) == Decimal("500.00")


def test_customer_cannot_access_another_customers_account(customer_client):
    # Register a second customer.
    registration = customer_client.post(
        "/users",
        json={
            "full_name": "Second Workflow Customer",
            "email": "second.workflow@example.com",
            "password": "SecondPassword@123",
        },
    )
    assert registration.status_code == 201

    # Log in as the second customer.
    login = customer_client.post(
        "/auth/login",
        json={"email": "second.workflow@example.com", "password": "SecondPassword@123"},
    )
    assert login.status_code == 200

    second_token = login.json()["access_token"]

    # Create an account as the second customer.
    account_response = customer_client.post(
        "/accounts",
        json={"account_name": "Second Customer Account", "currency": "INR"},
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert account_response.status_code == 201

    second_account_id = account_response.json()["id"]

    # The original customer must not access that account.
    response = customer_client.get(f"/accounts/{second_account_id}")

    assert response.status_code == 404
