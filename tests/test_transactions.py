def create_second_account(customer_client):
    response = customer_client.post(
        "/accounts", json={"account_name": "Second Savings Account", "currency": "INR"}
    )

    assert response.status_code == 201

    return response.json()


def test_successful_deposit(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "deposit-test-001"},
        json={"amount": "5000.00"},
    )

    assert response.status_code == 201

    transaction = response.json()

    assert transaction["amount"] == "5000.00"
    assert transaction["transaction_type"] == "deposit"
    assert transaction["status"] == "completed"
    assert transaction["destination_account_id"] == account_id


def test_deposit_updates_account_balance(customer_client, customer_account):
    account_id = customer_account["id"]

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "deposit-test-002"},
        json={"amount": "5000.00"},
    )

    response = customer_client.get(f"/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["balance"] == "5000.00"


def test_duplicate_deposit_does_not_update_balance_twice(
    customer_client, customer_account
):
    account_id = customer_account["id"]

    headers = {"Idempotency-Key": "deposit-duplicate-001"}
    payload = {"amount": "5000.00"}

    first_response = customer_client.post(
        f"/accounts/{account_id}/deposit", headers=headers, json=payload
    )

    second_response = customer_client.post(
        f"/accounts/{account_id}/deposit", headers=headers, json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["id"] == second_response.json()["id"]

    account_response = customer_client.get(f"/accounts/{account_id}")

    assert account_response.json()["balance"] == "5000.00"


def test_duplicate_deposit_with_different_amount_returns_conflict(
    customer_client, customer_account
):
    account_id = customer_account["id"]
    headers = {"Idempotency-Key": "deposit-conflict-001"}

    customer_client.post(
        f"/accounts/{account_id}/deposit", headers=headers, json={"amount": "5000.00"}
    )

    response = customer_client.post(
        f"/accounts/{account_id}/deposit", headers=headers, json={"amount": "7000.00"}
    )

    assert response.status_code == 409


def test_deposit_rejects_zero_amount(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "deposit-invalid-001"},
        json={"amount": "0.00"},
    )

    assert response.status_code == 422


def test_successful_withdrawal(customer_client, customer_account):
    account_id = customer_account["id"]

    # Deposit money first
    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "withdraw-setup-001"},
        json={"amount": "10000.00"},
    )

    response = customer_client.post(
        f"/accounts/{account_id}/withdraw",
        headers={"Idempotency-Key": "withdraw-test-001"},
        json={"amount": "3000.00"},
    )

    assert response.status_code == 201

    transaction = response.json()

    assert transaction["amount"] == "3000.00"
    assert transaction["transaction_type"] == "withdrawal"
    assert transaction["status"] == "completed"
    assert transaction["source_account_id"] == account_id


def test_withdrawal_updates_account_balance(customer_client, customer_account):
    account_id = customer_account["id"]

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "withdraw-setup-002"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{account_id}/withdraw",
        headers={"Idempotency-Key": "withdraw-test-002"},
        json={"amount": "4000.00"},
    )

    response = customer_client.get(f"/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["balance"] == "6000.00"


def test_withdrawal_rejects_insufficient_balance(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.post(
        f"/accounts/{account_id}/withdraw",
        headers={"Idempotency-Key": "withdraw-invalid-001"},
        json={"amount": "5000.00"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient account balance"


def test_duplicate_withdrawal_does_not_deduct_twice(customer_client, customer_account):
    account_id = customer_account["id"]

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "withdraw-setup-003"},
        json={"amount": "10000.00"},
    )

    headers = {"Idempotency-Key": "withdraw-duplicate-001"}
    payload = {"amount": "3000.00"}

    first_response = customer_client.post(
        f"/accounts/{account_id}/withdraw", headers=headers, json=payload
    )

    second_response = customer_client.post(
        f"/accounts/{account_id}/withdraw", headers=headers, json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["id"] == second_response.json()["id"]

    account_response = customer_client.get(f"/accounts/{account_id}")

    assert account_response.json()["balance"] == "7000.00"


def test_duplicate_withdrawal_with_different_amount_returns_conflict(
    customer_client, customer_account
):
    account_id = customer_account["id"]

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "withdraw-setup-004"},
        json={"amount": "10000.00"},
    )

    headers = {"Idempotency-Key": "withdraw-conflict-001"}

    customer_client.post(
        f"/accounts/{account_id}/withdraw", headers=headers, json={"amount": "2000.00"}
    )

    response = customer_client.post(
        f"/accounts/{account_id}/withdraw", headers=headers, json={"amount": "4000.00"}
    )

    assert response.status_code == 409


def test_withdrawal_rejects_zero_amount(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.post(
        f"/accounts/{account_id}/withdraw",
        headers={"Idempotency-Key": "withdraw-invalid-002"},
        json={"amount": "0.00"},
    )

    assert response.status_code == 422


def test_successful_transfer(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-001"},
        json={"amount": "10000.00"},
    )

    response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "transfer-test-001"},
        json={"destination_account_id": destination["id"], "amount": "3000.00"},
    )

    assert response.status_code == 201

    transaction = response.json()

    assert transaction["transaction_type"] == "transfer"
    assert transaction["amount"] == "3000.00"
    assert transaction["source_account_id"] == source_id
    assert transaction["destination_account_id"] == destination["id"]
    assert transaction["status"] == "completed"


def test_transfer_deducts_source_balance(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-002"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "transfer-test-002"},
        json={"destination_account_id": destination["id"], "amount": "4000.00"},
    )

    response = customer_client.get(f"/accounts/{source_id}")

    assert response.status_code == 200
    assert response.json()["balance"] == "6000.00"


def test_transfer_credits_destination_balance(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-003"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "transfer-test-003"},
        json={"destination_account_id": destination["id"], "amount": "4000.00"},
    )

    response = customer_client.get(f"/accounts/{destination['id']}")

    assert response.status_code == 200
    assert response.json()["balance"] == "4000.00"


def test_transfer_creates_transaction_record(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-004"},
        json={"amount": "10000.00"},
    )

    transfer_response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "transfer-test-004"},
        json={"destination_account_id": destination["id"], "amount": "2000.00"},
    )

    transaction_id = transfer_response.json()["id"]

    response = customer_client.get(f"/accounts/{source_id}/transactions")

    assert response.status_code == 200

    transactions = response.json()

    matching_transactions = [
        transaction
        for transaction in transactions
        if transaction["id"] == transaction_id
    ]

    assert len(matching_transactions) == 1


def test_transfer_rejects_insufficient_balance(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "transfer-invalid-001"},
        json={"destination_account_id": destination["id"], "amount": "5000.00"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient account balance"


def test_transfer_rejects_same_account(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.post(
        f"/accounts/{account_id}/transfer",
        headers={"Idempotency-Key": "transfer-invalid-002"},
        json={"destination_account_id": account_id, "amount": "1000.00"},
    )

    assert response.status_code == 400


def test_transfer_rejects_nonexistent_destination(customer_client, customer_account):
    source_id = customer_account["id"]

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-005"},
        json={"amount": "10000.00"},
    )

    response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "transfer-invalid-003"},
        json={"destination_account_id": 999999999, "amount": "1000.00"},
    )

    assert response.status_code == 404


def test_transfer_rejects_different_currencies(customer_client, customer_account):
    source_id = customer_account["id"]

    destination_response = customer_client.post(
        "/accounts", json={"account_name": "USD Account", "currency": "USD"}
    )

    assert destination_response.status_code == 201

    destination_id = destination_response.json()["id"]

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-006"},
        json={"amount": "10000.00"},
    )

    response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "transfer-invalid-004"},
        json={"destination_account_id": destination_id, "amount": "1000.00"},
    )

    assert response.status_code == 400


def test_duplicate_transfer_does_not_transfer_twice(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-007"},
        json={"amount": "10000.00"},
    )

    headers = {"Idempotency-Key": "transfer-duplicate-001"}

    payload = {"destination_account_id": destination["id"], "amount": "3000.00"}

    first_response = customer_client.post(
        f"/accounts/{source_id}/transfer", headers=headers, json=payload
    )

    second_response = customer_client.post(
        f"/accounts/{source_id}/transfer", headers=headers, json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["id"] == second_response.json()["id"]

    source_response = customer_client.get(f"/accounts/{source_id}")

    destination_response = customer_client.get(f"/accounts/{destination['id']}")

    assert source_response.json()["balance"] == "7000.00"
    assert destination_response.json()["balance"] == "3000.00"


def test_duplicate_transfer_with_different_amount_returns_conflict(
    customer_client, customer_account
):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "transfer-setup-008"},
        json={"amount": "10000.00"},
    )

    headers = {"Idempotency-Key": "transfer-conflict-001"}

    customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers=headers,
        json={"destination_account_id": destination["id"], "amount": "2000.00"},
    )

    response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers=headers,
        json={"destination_account_id": destination["id"], "amount": "4000.00"},
    )

    assert response.status_code == 409


def test_retrieve_transaction_history(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.get(f"/accounts/{account_id}/transactions")

    assert response.status_code == 200
    assert response.json() == []


def test_deposit_appears_in_transaction_history(customer_client, customer_account):
    account_id = customer_account["id"]

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "history-deposit-001"},
        json={"amount": "5000.00"},
    )

    response = customer_client.get(f"/accounts/{account_id}/transactions")

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 1
    assert transactions[0]["transaction_type"] == "deposit"
    assert transactions[0]["amount"] == "5000.00"


def test_withdrawal_appears_in_transaction_history(customer_client, customer_account):
    account_id = customer_account["id"]

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "history-setup-001"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{account_id}/withdraw",
        headers={"Idempotency-Key": "history-withdraw-001"},
        json={"amount": "3000.00"},
    )

    response = customer_client.get(f"/accounts/{account_id}/transactions")

    assert response.status_code == 200

    transactions = response.json()

    withdrawal_transactions = [
        transaction
        for transaction in transactions
        if transaction["transaction_type"] == "withdrawal"
    ]

    assert len(withdrawal_transactions) == 1
    assert withdrawal_transactions[0]["amount"] == "3000.00"


def test_transfer_appears_in_source_history(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "history-setup-002"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "history-transfer-001"},
        json={"destination_account_id": destination["id"], "amount": "2000.00"},
    )

    response = customer_client.get(f"/accounts/{source_id}/transactions")

    assert response.status_code == 200

    transfers = [
        transaction
        for transaction in response.json()
        if transaction["transaction_type"] == "transfer"
    ]

    assert len(transfers) == 1
    assert transfers[0]["source_account_id"] == source_id
    assert transfers[0]["destination_account_id"] == destination["id"]


def test_transfer_appears_in_destination_history(customer_client, customer_account):
    source_id = customer_account["id"]
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "history-setup-003"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": "history-transfer-002"},
        json={"destination_account_id": destination["id"], "amount": "2500.00"},
    )

    response = customer_client.get(f"/accounts/{destination['id']}/transactions")

    assert response.status_code == 200

    transfers = [
        transaction
        for transaction in response.json()
        if transaction["transaction_type"] == "transfer"
    ]

    assert len(transfers) == 1
    assert transfers[0]["destination_account_id"] == destination["id"]
    assert transfers[0]["source_account_id"] == source_id


def test_transaction_history_is_newest_first(customer_client, customer_account):
    account_id = customer_account["id"]

    first_response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "history-order-001"},
        json={"amount": "1000.00"},
    )

    second_response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "history-order-002"},
        json={"amount": "2000.00"},
    )

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    response = customer_client.get(f"/accounts/{account_id}/transactions")

    assert response.status_code == 200

    transactions = response.json()

    assert transactions[0]["id"] == second_id
    assert transactions[1]["id"] == first_id


def test_transaction_history_pagination(customer_client, customer_account):
    account_id = customer_account["id"]

    amounts = ["1000.00", "2000.00", "3000.00"]
    transaction_ids = []

    for index, amount in enumerate(amounts):
        response = customer_client.post(
            f"/accounts/{account_id}/deposit",
            headers={"Idempotency-Key": f"history-pagination-{index:03d}"},
            json={"amount": amount},
        )

        assert response.status_code == 201
        transaction_ids.append(response.json()["id"])

    response = customer_client.get(
        f"/accounts/{account_id}/transactions", params={"skip": 1, "limit": 1}
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 1
    assert transactions[0]["id"] == transaction_ids[1]


def test_customer_cannot_access_another_customers_transaction_history(
    customer_client, customer_account
):
    first_account_id = customer_account["id"]

    # Create a second customer
    register_response = customer_client.post(
        "/users",
        json={
            "full_name": "Another Customer",
            "email": "another.customer@example.com",
            "password": "AnotherPassword@123",
        },
    )

    assert register_response.status_code == 201

    # Create the second customer's account using a separate token
    login_response = customer_client.post(
        "/auth/login",
        json={
            "email": "another.customer@example.com",
            "password": "AnotherPassword@123",
        },
    )

    assert login_response.status_code == 200

    second_token = login_response.json()["access_token"]

    response = customer_client.get(
        f"/accounts/{first_account_id}/transactions",
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert response.status_code == 404


def test_deposit_key_cannot_be_reused_for_withdrawal(customer_client, customer_account):
    account_id = customer_account["id"]
    key = "cross-operation-001"

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "cross-setup-001"},
        json={"amount": "10000.00"},
    )

    deposit_response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert deposit_response.status_code == 201

    response = customer_client.post(
        f"/accounts/{account_id}/withdraw",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert response.status_code == 409


def test_withdrawal_key_cannot_be_reused_for_deposit(customer_client, customer_account):
    account_id = customer_account["id"]
    key = "cross-operation-002"

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "cross-setup-002"},
        json={"amount": "10000.00"},
    )

    withdrawal_response = customer_client.post(
        f"/accounts/{account_id}/withdraw",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert withdrawal_response.status_code == 201

    response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert response.status_code == 409


def test_deposit_key_cannot_be_reused_for_another_account(
    customer_client, customer_account
):
    first_account_id = customer_account["id"]
    second_account = create_second_account(customer_client)

    key = "cross-account-001"

    first_response = customer_client.post(
        f"/accounts/{first_account_id}/deposit",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert first_response.status_code == 201

    response = customer_client.post(
        f"/accounts/{second_account['id']}/deposit",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert response.status_code == 409


def test_withdrawal_key_cannot_be_reused_for_another_account(
    customer_client, customer_account
):
    first_account_id = customer_account["id"]
    second_account = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{first_account_id}/deposit",
        headers={"Idempotency-Key": "cross-setup-003"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{second_account['id']}/deposit",
        headers={"Idempotency-Key": "cross-setup-004"},
        json={"amount": "10000.00"},
    )

    key = "cross-account-002"

    first_response = customer_client.post(
        f"/accounts/{first_account_id}/withdraw",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert first_response.status_code == 201

    response = customer_client.post(
        f"/accounts/{second_account['id']}/withdraw",
        headers={"Idempotency-Key": key},
        json={"amount": "2000.00"},
    )

    assert response.status_code == 409


def test_transfer_key_cannot_be_reused_for_another_destination(
    customer_client, customer_account
):
    source_id = customer_account["id"]
    first_destination = create_second_account(customer_client)
    second_destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{source_id}/deposit",
        headers={"Idempotency-Key": "cross-setup-005"},
        json={"amount": "10000.00"},
    )

    key = "cross-transfer-001"

    first_response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": key},
        json={"destination_account_id": first_destination["id"], "amount": "2000.00"},
    )

    assert first_response.status_code == 201

    response = customer_client.post(
        f"/accounts/{source_id}/transfer",
        headers={"Idempotency-Key": key},
        json={"destination_account_id": second_destination["id"], "amount": "2000.00"},
    )

    assert response.status_code == 409


def test_transfer_key_cannot_be_reused_for_another_source(
    customer_client, customer_account
):
    first_source_id = customer_account["id"]
    second_source = create_second_account(customer_client)
    destination = create_second_account(customer_client)

    customer_client.post(
        f"/accounts/{first_source_id}/deposit",
        headers={"Idempotency-Key": "cross-setup-006"},
        json={"amount": "10000.00"},
    )

    customer_client.post(
        f"/accounts/{second_source['id']}/deposit",
        headers={"Idempotency-Key": "cross-setup-007"},
        json={"amount": "10000.00"},
    )

    key = "cross-transfer-002"

    first_response = customer_client.post(
        f"/accounts/{first_source_id}/transfer",
        headers={"Idempotency-Key": key},
        json={"destination_account_id": destination["id"], "amount": "2000.00"},
    )

    assert first_response.status_code == 201

    response = customer_client.post(
        f"/accounts/{second_source['id']}/transfer",
        headers={"Idempotency-Key": key},
        json={"destination_account_id": destination["id"], "amount": "2000.00"},
    )

    assert response.status_code == 409


def test_deposit_rejects_missing_idempotency_key(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.post(
        f"/accounts/{account_id}/deposit", json={"amount": "1000.00"}
    )

    assert response.status_code == 422


def test_deposit_rejects_short_idempotency_key(customer_client, customer_account):
    account_id = customer_account["id"]

    response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": "short12"},
        json={"amount": "1000.00"},
    )

    assert response.status_code == 422


def test_another_customer_cannot_replay_deposit(
    customer_client,
    customer_account,
):
    account_id = customer_account["id"]
    idempotency_key = "secure-replay-001"

    first_response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": idempotency_key},
        json={"amount": "1000.00"},
    )

    assert first_response.status_code == 201

    # Register another customer.
    registration = customer_client.post(
        "/users",
        json={
            "full_name": "Second Security Customer",
            "email": "replay.security@example.com",
            "password": "SecurityPassword@123",
        },
    )

    assert registration.status_code == 201

    login = customer_client.post(
        "/auth/login",
        json={
            "email": "replay.security@example.com",
            "password": "SecurityPassword@123",
        },
    )

    assert login.status_code == 200

    second_token = login.json()["access_token"]

    # Attempt to replay the first customer's transaction.
    response = customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={
            "Idempotency-Key": idempotency_key,
            "Authorization": f"Bearer {second_token}",
        },
        json={"amount": "1000.00"},
    )

    assert response.status_code == 404


def test_unauthorized_replay_does_not_change_balance(
    customer_client,
    customer_account,
):
    account_id = customer_account["id"]
    idempotency_key = "secure-replay-002"

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={"Idempotency-Key": idempotency_key},
        json={"amount": "2000.00"},
    )

    registration = customer_client.post(
        "/users",
        json={
            "full_name": "Replay Protection Customer",
            "email": "replay.protection@example.com",
            "password": "ProtectionPassword@123",
        },
    )

    assert registration.status_code == 201

    login = customer_client.post(
        "/auth/login",
        json={
            "email": "replay.protection@example.com",
            "password": "ProtectionPassword@123",
        },
    )

    second_token = login.json()["access_token"]

    customer_client.post(
        f"/accounts/{account_id}/deposit",
        headers={
            "Idempotency-Key": idempotency_key,
            "Authorization": f"Bearer {second_token}",
        },
        json={"amount": "2000.00"},
    )

    # Original customer still owns the account.
    balance_response = customer_client.get(f"/accounts/{account_id}")

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == "2000.00"
