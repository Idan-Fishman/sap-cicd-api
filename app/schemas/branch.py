from uuid import UUID
from typing import Optional

from pydantic import BaseModel


# Shared properties
class BranchBase(BaseModel):
    title: Optional[str]
    description: Optional[str]


# Properties to receive via API on creation
class BranchCreate(BranchBase):
    title: str


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
    pass
