"""
Adds support for alembic's migrations autogenrate feature.
"""

from .base import Base

# Import your models here
from .branch import Branch
from .change_request import ChangeRequest
