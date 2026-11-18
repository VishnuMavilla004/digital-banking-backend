from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_non_negative_balance"),
        CheckConstraint(
            "currency ~ '^[A-Z]{3}$'",
            name="check_valid_account_currency",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), default=Decimal("0.00"), nullable=False
    )

    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    owner: Mapped["User"] = relationship(back_populates="accounts")

    account_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
