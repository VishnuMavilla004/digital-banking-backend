from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    account_name: str
    currency: str = Field(
        default="INR", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"
    )


class AccountUpdate(BaseModel):
    account_name: str | None = None


class AccountResponse(BaseModel):
    id: int
    account_number: str
    user_id: int
    account_name: str | None
    balance: Decimal
    currency: str

    model_config = ConfigDict(from_attributes=True)
