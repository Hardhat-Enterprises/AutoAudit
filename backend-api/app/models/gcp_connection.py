"""GCP connection model stub."""

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GCPConnection(Base):
    """GCP connection stub (columns added when implemented)."""

    __tablename__ = "gcp_connection"

    id: Mapped[int] = mapped_column(primary_key=True)
