"""
Module for operations specific to IElement interface.

Classes
-------
- `Text` - Extracts text from element - most common operation.
- `Href` - Extracts href attribute from element.
- `Parent` - Extracts parent of element.

These components are design to be used for processing html tags and extracting
desired information. They can be used in combination with selectors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union, overload

from soupsavvy.base import BaseOperation, OperationSearcherMixin, SoupSelector
from soupsavvy.interfaces import IElement

if TYPE_CHECKING:
    from soupsavvy.operations.general import OperationPipeline
    from soupsavvy.selectors.logical import SelectorList


class Text(OperationSearcherMixin):
    """
    Operation to extract text from `bs4.Tag`.
    Wrapper of most common operation used in web scraping.

    Example
    -------
    >>> from soupsavvy.operations import Text
    ... operation = Text()
    ... operation.execute(tag)
    "Extracted text from the tag"

    Wrapper for `bs4.Tag.get_text` method, that exposes all its options,
    and imitates its default behavior.

    Implements `TagSearcher` interface for convenience. It has find methods
    that can be used to extract text from provided tag.

    Example
    -------
    >>> from soupsavvy.operations import Text
    ... operation = Text()
    ... operation.find(tag)
    "Text"
    """

    def _execute(self, arg: IElement) -> str:
        """Extracts text from `bs4.Tag`."""
        return arg.text

    def __eq__(self, x: Any) -> bool:
        # equal only if separator and strip are the same
        return isinstance(x, Text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Href(OperationSearcherMixin):
    """
    Operation to extract href attribute from `bs4.Tag`.
    Wrapper of one of the common operation used in web scraping.
    If href attribute is not present, returns None.

    Example
    -------
    >>> from soupsavvy.operations import Href
    ... operation = Href()
    ... operation.execute(tag)
    "www.example.com"

    Implements `TagSearcher` interface for convenience. It has find methods
    that can be used to extract href from provided tag.

    Example
    -------
    >>> from soupsavvy.operations import Href
    ... operation = Href()
    ... operation.find(tag)
    "www.example.com"
    """

    _ATTRIBUTE_NAME = "href"

    def _execute(self, arg: IElement) -> Optional[str]:
        """
        Extracts href attribute from a BeautifulSoup Tag.
        If attribute is not present, returns None.
        """
        return arg.get_attribute(self._ATTRIBUTE_NAME)

    def __eq__(self, x: Any) -> bool:
        # equal only if both are instances of Href
        return isinstance(x, Href)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Parent(BaseOperation, SoupSelector):
    """
    Operation to extract parent of `bs4.Tag`.

    Example
    -------
    >>> from soupsavvy.operations import Parent
    ... operation = Parent()
    ... operation.execute(tag)
    "<div>...</div>"

    Implements `SoupSelector` interface for convenience and can be used
    to extract parent of a provided tag without any conditions.

    Example
    -------
    >>> from soupsavvy.operations import Parent
    ... operation = Parent()
    ... operation.find(tag)
    "<div>--tag--</div>"

    `Parent` has `BaseOperation` higher in MRO than `SoupSelector`, so, using pipe
    operator `|` on `Parent` object will result in `OperationPipeline` instance.

    Example
    -------
    >>> from soupsavvy.operations import Parent
    ... operation = Parent() | Parent()
    ... operation.execute(tag)
    "<div><div>--tag--</div></div>"

    Notes
    -----
    If element does not have parent, returns None.
    """

    def _execute(self, arg: IElement) -> Optional[IElement]:
        """Extracts parent of `bs4.Tag`."""
        return arg.parent

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        return [self.execute(tag)]

    def __eq__(self, x: Any) -> bool:
        # equal only if both are instances of Parent
        return isinstance(x, Parent)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @overload  # type: ignore
    def __or__(self, other: BaseOperation) -> OperationPipeline: ...

    @overload
    def __or__(self, other: SoupSelector) -> SelectorList: ...

    def __or__(
        self, other: Union[BaseOperation, SoupSelector]
    ) -> Union[OperationPipeline, SelectorList]:
        if isinstance(other, SoupSelector):
            return SoupSelector.__or__(self, other)

        return BaseOperation.__or__(self, other)
