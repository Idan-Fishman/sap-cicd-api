from typing import Any

from sqlalchemy.exc import IntegrityError

from app.models import Branch
from app.schemas import BranchCreate, BranchUpdate
from .base import BaseCRUD


class BranchCRUD(BaseCRUD[Branch, BranchCreate, BranchUpdate]):
    @staticmethod
    def integrity_error(error: IntegrityError) -> dict[str, Any]:
        if error.orig.pgcode == "23505":  # UniqueViolationError is 23505
            error_args_str = "".join(error.orig.args)

            if error_args_str.find("branch_title_key") != -1:
                return {
                    "loc": ["body", "title"],
                    "msg": "value already exists",
                }
        raise error


branch = BranchCRUD(model=Branch)
