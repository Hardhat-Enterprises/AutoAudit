"""AWS connection model stub."""

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AWSConnection(Base):
    """AWS connection stub (columns added when implemented)."""

    __tablename__ = "aws_connection"

    id: Mapped[int] = mapped_column(primary_key=True)
