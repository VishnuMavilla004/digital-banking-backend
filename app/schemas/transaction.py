from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MoneyOperationRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=16, decimal_places=2)


class TransferRequest(BaseModel):
    destination_account_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=16, decimal_places=2)


class TransactionResponse(BaseModel):
    id: int
    source_account_id: int | None
    destination_account_id: int | None
    amount: Decimal
    transaction_type: str
    status: str

    model_config = ConfigDict(from_attributes=True)
