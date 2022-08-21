from uuid import uuid4

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class Branch(Base):
    __tablename__ = "branch"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    title = Column(String(length=100), nullable=False, unique=True)
    description = Column(String(length=400))

    change_requests = relationship(
        "ChangeRequest",
        lazy="selectin",
        order_by="ChangeRequest.created_at",
    )
