from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Account, Transaction


def test_database_rejects_invalid_transaction_type(
    db_session,
    customer_account,
):
    transaction = Transaction(
        source_account_id=None,
        destination_account_id=customer_account["id"],
        amount=Decimal("100.00"),
        transaction_type="invalid_type",
        status="completed",
    )

    db_session.add(transaction)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_rejects_invalid_transaction_status(
    db_session,
    customer_account,
):
    transaction = Transaction(
        source_account_id=None,
        destination_account_id=customer_account["id"],
        amount=Decimal("100.00"),
        transaction_type="deposit",
        status="unknown_status",
    )

    db_session.add(transaction)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_rejects_invalid_account_currency(
    db_session,
    customer_account,
):
    account = Account(
        account_number=f"1001{uuid4().hex[:8]}",
        user_id=customer_account["user_id"],
        account_name="Invalid Currency Account",
        balance=Decimal("0.00"),
        currency="inr",
    )

    db_session.add(account)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
