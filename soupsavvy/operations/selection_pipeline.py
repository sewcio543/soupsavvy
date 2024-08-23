from __future__ import annotations

from typing import Any, Optional

from bs4 import Tag

from soupsavvy.interfaces import Comparable, TagSearcher
from soupsavvy.operations.base import BaseOperation, check_operator
from soupsavvy.selectors.base import SoupSelector


class SelectionPipeline(TagSearcher, Comparable):

    def __init__(self, selector: SoupSelector, operation: BaseOperation) -> None:
        self.selector = selector
        self.operation = operation

    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        return self.operation.execute(
            self.selector.find(tag, strict=strict, recursive=recursive)
        )

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:

        return [
            self.operation.execute(element)
            for element in self.selector.find_all(tag, recursive=recursive, limit=limit)
        ]

    def __or__(self, x: Any) -> SelectionPipeline:
        x = check_operator(x)
        operation = self.operation | x
        return SelectionPipeline(selector=self.selector, operation=operation)

    def __eq__(self, x) -> bool:
        if not isinstance(x, SelectionPipeline):
            return False

        return self.selector == x.selector and self.operation == x.operation
