import logging
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Account, Transaction

logger = logging.getLogger(__name__)


def _find_existing_transaction(db: Session, idempotency_key: str):
    statement = select(Transaction).where(
        Transaction.idempotency_key == idempotency_key
    )
    return db.scalars(statement).first()


def _is_same_request(
    existing: Transaction,
    transaction_type: str,
    source_account_id: int | None,
    destination_account_id: int | None,
    amount: Decimal,
) -> bool:
    return (
        existing.transaction_type == transaction_type
        and existing.source_account_id == source_account_id
        and existing.destination_account_id == destination_account_id
        and existing.amount == amount
    )


def _get_idempotent_replay(
    db: Session,
    idempotency_key: str,
    transaction_type: str,
    source_account_id: int | None,
    destination_account_id: int | None,
    amount: Decimal,
    user_id: int,
    authorized_account_id: int,
):
    existing = _find_existing_transaction(db, idempotency_key)

    if existing is None:
        return None

    # Verify that the requesting user owns the relevant account.
    owned_account = db.scalar(
        select(Account.id).where(
            Account.id == authorized_account_id,
            Account.user_id == user_id,
        )
    )

    if owned_account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    if _is_same_request(
        existing,
        transaction_type,
        source_account_id,
        destination_account_id,
        amount,
    ):
        logger.info(
            "Idempotent request replayed | transaction_id=%s",
            existing.id,
        )
        return existing

    logger.warning(
        "Idempotency conflict | existing_transaction_id=%s",
        existing.id,
    )

    raise HTTPException(
        status_code=409,
        detail="Idempotency key already used for another request",
    )


def deposit_money(
    db: Session, account_id: int, user_id: int, amount: Decimal, idempotency_key: str
):
    existing = _get_idempotent_replay(
        db=db,
        idempotency_key=idempotency_key,
        transaction_type="deposit",
        source_account_id=None,
        destination_account_id=account_id,
        amount=amount,
        user_id=user_id,
        authorized_account_id=account_id,
    )

    if existing is not None:
        return existing

    account = db.scalar(
        select(Account)
        .where(Account.id == account_id, Account.user_id == user_id)
        .with_for_update()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    account.balance += amount

    transaction = Transaction(
        source_account_id=None,
        destination_account_id=account.id,
        amount=amount,
        transaction_type="deposit",
        status="completed",
        idempotency_key=idempotency_key,
    )

    db.add(transaction)

    try:
        db.commit()
        db.refresh(transaction)

        logger.info(
            "Deposit completed | account_id=%s | transaction_id=%s",
            account.id,
            transaction.id,
        )

        return transaction

    except IntegrityError:
        db.rollback()

        existing = _get_idempotent_replay(
            db=db,
            idempotency_key=idempotency_key,
            transaction_type="deposit",
            source_account_id=None,
            destination_account_id=account_id,
            amount=amount,
            user_id=user_id,
            authorized_account_id=account_id,
        )

        if existing is None:
            raise

        return existing


def withdraw_money(
    db: Session, account_id: int, user_id: int, amount: Decimal, idempotency_key: str
):
    existing = _get_idempotent_replay(
        db=db,
        idempotency_key=idempotency_key,
        transaction_type="withdrawal",
        source_account_id=account_id,
        destination_account_id=None,
        amount=amount,
        user_id=user_id,
        authorized_account_id=account_id,
    )

    if existing is not None:
        return existing

    account = db.scalar(
        select(Account)
        .where(Account.id == account_id, Account.user_id == user_id)
        .with_for_update()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < amount:
        logger.warning(
            "Withdrawal rejected: insufficient funds | account_id=%s", account_id
        )
        raise HTTPException(status_code=400, detail="Insufficient account balance")

    account.balance -= amount

    transaction = Transaction(
        source_account_id=account.id,
        destination_account_id=None,
        amount=amount,
        transaction_type="withdrawal",
        status="completed",
        idempotency_key=idempotency_key,
    )

    db.add(transaction)

    try:
        db.commit()
        db.refresh(transaction)

        logger.info(
            "Withdrawal completed | account_id=%s | transaction_id=%s",
            account.id,
            transaction.id,
        )

        return transaction

    except IntegrityError:
        db.rollback()

        existing = _get_idempotent_replay(
            db=db,
            idempotency_key=idempotency_key,
            transaction_type="withdrawal",
            source_account_id=account_id,
            destination_account_id=None,
            amount=amount,
            user_id=user_id,
            authorized_account_id=account_id,
        )


def transfer_money(
    db: Session,
    source_account_id: int,
    user_id: int,
    destination_account_id: int,
    amount: Decimal,
    idempotency_key: str,
):
    existing = _get_idempotent_replay(
        db=db,
        idempotency_key=idempotency_key,
        transaction_type="transfer",
        source_account_id=source_account_id,
        destination_account_id=destination_account_id,
        amount=amount,
        user_id=user_id,
        authorized_account_id=source_account_id,
    )

    if existing is not None:
        return existing

    if source_account_id == destination_account_id:
        raise HTTPException(
            status_code=400, detail="Cannot transfer money to the same account"
        )

    # Lock accounts in a consistent order to reduce deadlock risk.
    account_ids = sorted([source_account_id, destination_account_id])

    locked_accounts = db.scalars(
        select(Account)
        .where(Account.id.in_(account_ids))
        .order_by(Account.id)
        .with_for_update()
    ).all()

    accounts_by_id = {account.id: account for account in locked_accounts}

    source_account = accounts_by_id.get(source_account_id)
    destination_account = accounts_by_id.get(destination_account_id)

    if source_account is None or source_account.user_id != user_id:
        raise HTTPException(status_code=404, detail="Source account not found")

    if destination_account is None:
        raise HTTPException(status_code=404, detail="Destination account not found")

    if source_account.currency != destination_account.currency:
        raise HTTPException(
            status_code=400, detail="Currency mismatch between accounts"
        )

    if source_account.balance < amount:
        logger.warning(
            "Transfer rejected: insufficient funds | source_account_id=%s",
            source_account_id,
        )
        raise HTTPException(status_code=400, detail="Insufficient account balance")

    source_account.balance -= amount
    destination_account.balance += amount

    transaction = Transaction(
        source_account_id=source_account.id,
        destination_account_id=destination_account.id,
        amount=amount,
        transaction_type="transfer",
        status="completed",
        idempotency_key=idempotency_key,
    )

    db.add(transaction)

    try:
        db.commit()
        db.refresh(transaction)

        logger.info(
            "Transfer completed | source_account_id=%s | "
            "destination_account_id=%s | transaction_id=%s",
            source_account.id,
            destination_account.id,
            transaction.id,
        )

        return transaction
    except IntegrityError:
        db.rollback()

        existing = _get_idempotent_replay(
            db=db,
            idempotency_key=idempotency_key,
            transaction_type="transfer",
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            amount=amount,
            user_id=user_id,
            authorized_account_id=source_account_id,
        )

        if existing is None:
            raise

        return existing
