from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
    """OAuth account linked to a User (e.g., Google identity)."""

    __tablename__ = "oauth_account"
    __table_args__ = (
        UniqueConstraint(
            "oauth_name",
            "account_id",
            name="uq_oauth_account_oauth_name_account_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")



