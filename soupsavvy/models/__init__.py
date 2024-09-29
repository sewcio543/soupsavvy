"""
Package with models for defining search schemas with operations and selectors.

Classes
-------
- `BaseModel` - Base class for defining search schemas.
- `Field` - Field configuration for search schema.
- `MigrationSchema` - Configuration of model migration.
- `All` - Wrapper to find all information matching criteria.
- `Default` - Wrapper to set default value if information is not found.
- `Required` - Wrapper to enforce that information must be found.
"""

from .base import BaseModel, Field, MigrationSchema, post
from .wrappers import All, Default, Required

__all__ = [
    "BaseModel",
    "All",
    "Default",
    "Required",
    "post",
    "Field",
    "MigrationSchema",
]
