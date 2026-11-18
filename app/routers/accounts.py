import logging
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth_dependencies import get_current_user
from app.dependencies import get_db
from app.models import Account, Transaction, User
from app.schemas import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    MoneyOperationRequest,
    TransactionResponse,
    TransferRequest,
)
from app.services import deposit_money, transfer_money, withdraw_money

router = APIRouter(tags=["Accounts"])
logger = logging.getLogger(__name__)


def generate_account_number():
    return "1001" + "".join(secrets.choice("0123456789") for _ in range(8))


@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    max_attempts = 5

    for _ in range(max_attempts):
        account_number = generate_account_number()

        # Check whether the generated number already exists.
        existing_account = db.scalar(
            select(Account.id).where(Account.account_number == account_number)
        )

        if existing_account is not None:
            continue

        account = Account(
            account_number=account_number,
            user_id=current_user.id,
            account_name=account_data.account_name,
            currency=account_data.currency,
        )

        db.add(account)

        try:
            db.commit()

        except IntegrityError:
            db.rollback()

            # Determine whether the failure was an account-number collision.
            collision = db.scalar(
                select(Account.id).where(Account.account_number == account_number)
            )

            if collision is not None:
                continue

            # Preserve unrelated database errors.
            raise

        db.refresh(account)
        return account

    raise HTTPException(
        status_code=503,
        detail="Unable to generate a unique account number. Please try again.",
    )


@router.get("/accounts", response_model=list[AccountResponse])
def get_my_accounts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    statement = select(Account).where(Account.user_id == current_user.id)

    return db.scalars(statement).all()


@router.get("/accounts/{account_id}", response_model=AccountResponse)
def get_my_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Account).where(
        Account.id == account_id, Account.user_id == current_user.id
    )

    account = db.scalars(statement).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.patch("/accounts/{account_id}", response_model=AccountResponse)
def update_my_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Account).where(
        Account.id == account_id, Account.user_id == current_user.id
    )

    account = db.scalars(statement).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = account_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)

    return account


@router.post(
    "/accounts/{account_id}/deposit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def deposit(
    account_id: int,
    request: MoneyOperationRequest,
    idempotency_key: str = Header(
        ..., alias="Idempotency-Key", min_length=8, max_length=100
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return deposit_money(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
        amount=request.amount,
        idempotency_key=idempotency_key,
    )


@router.post(
    "/accounts/{account_id}/withdraw",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def withdraw(
    account_id: int,
    request: MoneyOperationRequest,
    idempotency_key: str = Header(
        ..., alias="Idempotency-Key", min_length=8, max_length=100
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return withdraw_money(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
        amount=request.amount,
        idempotency_key=idempotency_key,
    )


@router.post(
    "/accounts/{source_account_id}/transfer",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def transfer(
    source_account_id: int,
    request: TransferRequest,
    idempotency_key: str = Header(
        ..., alias="Idempotency-Key", min_length=8, max_length=100
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transfer_money(
        db=db,
        source_account_id=source_account_id,
        user_id=current_user.id,
        destination_account_id=request.destination_account_id,
        amount=request.amount,
        idempotency_key=idempotency_key,
    )


@router.get(
    "/accounts/{account_id}/transactions", response_model=list[TransactionResponse]
)
def get_account_transactions(
    account_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = db.scalars(
        select(Account).where(
            Account.id == account_id, Account.user_id == current_user.id
        )
    ).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    statement = (
        select(Transaction)
        .where(
            or_(
                Transaction.source_account_id == account_id,
                Transaction.destination_account_id == account_id,
            )
        )
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(statement).all()
