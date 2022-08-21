from datetime import datetime

from pytz import timezone
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class ChangeRequest(Base):
    __tablename__ = "change_request"

    number = Column(String(length=20), primary_key=True, index=True)

    type = Column(String(length=1), nullable=False)
    description = Column(String(length=75))
    status = Column(String(length=1), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(tz=timezone("Asia/Jerusalem")),
        nullable=False,
    )

    branch_id = Column(UUID(as_uuid=True), ForeignKey("branch.id"), nullable=False)
