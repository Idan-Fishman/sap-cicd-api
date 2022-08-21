from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StatusEnum(str, Enum):
    modifiable = "D"
    modifiable_protected = "L"
    release_standard = "O"
    released = "R"
    released_with_import_protection_for_repaired_objects = "N"


class TypeEnum(str, Enum):
    workbench = "K"
    customizing = "W"
    transport_of_copies = "T"


# Shared properties
class ChangeRequestBase(BaseModel):
    description: Optional[str]
    type: Optional[TypeEnum]


# Properties to receive via API on creation
class ChangeRequestCreate(ChangeRequestBase):
    number: str  # FIXME: use for development only, hovav's api should generate the number for you
    status: StatusEnum = StatusEnum.modifiable  # automaticly modifaible
    description: str
    type: TypeEnum


# Properties to receive via API on update
class ChangeRequestUpdate(ChangeRequestBase):
    pass


# Database serializer
class ChangeRequestBaseDB(ChangeRequestBase):
    number: str
    status: StatusEnum

    class Config:
        orm_mode = True


# Additional properties stored in DB
class ChangeRequestDB(ChangeRequestBaseDB):
    pass


# Additional properties to return via API
class ChangeRequest(ChangeRequestBaseDB):
    branch_id: UUID
