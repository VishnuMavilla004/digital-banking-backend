from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Account, Transaction, User
from app.security import hash_password
from app.services.banking import deposit_money, withdraw_money


def create_committed_test_account(test_engine, initial_balance="0.00"):
    """Create committed records visible to independent database sessions."""

    unique_id = uuid4().hex

    with Session(test_engine) as db:
        user = User(
            full_name="Concurrency Test User",
            email=f"concurrency_{unique_id}@example.com",
            password_hash=hash_password("TestPassword@123"),
            role="customer",
        )

        db.add(user)
        db.flush()

        account = Account(
            account_number=f"1001{unique_id[:8]}",
            user_id=user.id,
            account_name="Concurrency Test Account",
            balance=Decimal(initial_balance),
            currency="INR",
        )

        db.add(account)
        db.commit()

        return user.id, account.id


def test_concurrent_withdrawals_cannot_overdraw_account(test_engine):
    user_id, account_id = create_committed_test_account(
        test_engine,
        initial_balance="1000.00",
    )

    barrier = Barrier(2)

    def perform_withdrawal(index):
        with Session(test_engine) as db:
            barrier.wait(timeout=10)

            try:
                transaction = withdraw_money(
                    db=db,
                    account_id=account_id,
                    user_id=user_id,
                    amount=Decimal("700.00"),
                    idempotency_key=f"concurrent-withdraw-{uuid4().hex}",
                )

                return ("success", transaction.id)

            except HTTPException as exc:
                db.rollback()
                return ("rejected", exc.status_code)

            except Exception:
                db.rollback()
                raise

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(perform_withdrawal, index) for index in range(2)]

        results = [future.result(timeout=30) for future in futures]

    # Exactly one withdrawal should succeed.
    successful_requests = [result for result in results if result[0] == "success"]

    rejected_requests = [result for result in results if result[0] == "rejected"]

    assert len(successful_requests) == 1
    assert len(rejected_requests) == 1

    with Session(test_engine) as db:
        account = db.get(Account, account_id)

        transaction_count = db.scalar(
            select(func.count(Transaction.id)).where(
                Transaction.source_account_id == account_id,
                Transaction.transaction_type == "withdrawal",
            )
        )

        assert account.balance == Decimal("300.00")
        assert transaction_count == 1


def test_concurrent_duplicate_deposits_are_processed_once(test_engine):
    user_id, account_id = create_committed_test_account(test_engine)

    barrier = Barrier(2)
    shared_key = f"concurrent-deposit-{uuid4().hex}"

    def perform_deposit():
        with Session(test_engine) as db:
            barrier.wait(timeout=10)

            try:
                transaction = deposit_money(
                    db=db,
                    account_id=account_id,
                    user_id=user_id,
                    amount=Decimal("500.00"),
                    idempotency_key=shared_key,
                )

                return transaction.id

            except Exception:
                db.rollback()
                raise

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(perform_deposit) for _ in range(2)]

        transaction_ids = [future.result(timeout=30) for future in futures]

    # Both requests must resolve to the same transaction.
    assert transaction_ids[0] == transaction_ids[1]

    with Session(test_engine) as db:
        account = db.get(Account, account_id)

        transaction_count = db.scalar(
            select(func.count(Transaction.id)).where(
                Transaction.idempotency_key == shared_key
            )
        )

        assert account.balance == Decimal("500.00")
        assert transaction_count == 1
