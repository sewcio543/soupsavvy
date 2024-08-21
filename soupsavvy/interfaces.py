from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from bs4 import Tag


class Executable(ABC):
    @abstractmethod
    def execute(self, arg: Any) -> Any:
        """Execute the operation on the given argument."""
        pass


class Comparable(ABC):
    @abstractmethod
    def __eq__(self, x: Any) -> bool:
        pass


class TagSearcher(ABC):

    @abstractmethod
    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any: ...

    @abstractmethod
    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]: ...
