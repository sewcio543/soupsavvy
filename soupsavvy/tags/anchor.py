import operator
from typing import Callable

from bs4 import Tag

from soupsavvy.tags.base import SelectableSoup

Operator = Callable[[SelectableSoup, SelectableSoup], SelectableSoup]


class RelativeSelector(SelectableSoup):
    def __init__(self, operator: Operator, selector: SelectableSoup) -> None:
        self.operator = operator
        self.selector = selector

    def anchor(self, x: SelectableSoup) -> SelectableSoup:
        return self.operator(x, self.selector)

    def find_all(self, tag: Tag, recursive=True, limit=None) -> list[Tag]:
        message = (
            f"Not possible to find elements with {self.__class__.__name__}. "
            + "It needs to be anchored against another selector first. Use 'anchor' method."
        )
        raise NotImplementedError(message)


class _Anchor:

    def __gt__(self, x) -> RelativeSelector:
        return RelativeSelector(operator=operator.gt, selector=x)

    def __add__(self, x) -> RelativeSelector:
        return RelativeSelector(operator=operator.add, selector=x)

    def __mul__(self, x) -> RelativeSelector:
        return RelativeSelector(operator=operator.mul, selector=x)

    def __rshift__(self, x) -> RelativeSelector:
        return RelativeSelector(operator=operator.rshift, selector=x)


Anchor = _Anchor()
