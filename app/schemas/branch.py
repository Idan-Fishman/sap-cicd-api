from uuid import UUID
from typing import Optional

from pydantic import BaseModel

from .change_request import ChangeRequest

# Shared properties
class BranchBase(BaseModel):
    title: Optional[str]
    description: Optional[str]


# Properties to receive via API on creation
class BranchCreate(BranchBase):
    title: str


# Properties to receive via API on update
class BranchUpdate(BranchBase):
    pass


# Database serializer
class BranchBaseDB(BranchBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties stored in DB
class BranchDB(BranchBaseDB):
    pass


# Additional properties to return via API
class Branch(BranchBaseDB):
    change_requests: list[ChangeRequest]
