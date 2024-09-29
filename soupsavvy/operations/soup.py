"""
Module for operations specific to BeautifulSoup tags.

Classes
-------
- `Text` - Extracts text from `bs4.Tag` - most common operation.
- `Href` - Extracts href attribute from `bs4.Tag`
- `Parent` - Extracts parent of `bs4.Tag`

These components are design to be used for processing html tags and extracting
desired information. They can be used in combination with selectors.
"""

from typing import Any, Optional

from bs4 import Tag

from soupsavvy.base import BaseOperation, OperationSearcherMixin, SoupSelector


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

    def __init__(self, separator: str = "", strip: bool = False) -> None:
        """
        Initializes `Text` operation with optional separator and strip options.

        Parameters
        ----------
        separator : str, optional
            Separator used to join strings from multiple text nodes, by default "".
        strip : bool, optional
            Flag to strip the text nodes from whitespaces and newline characters,
            by default False.
        """
        self.separator = separator
        self.strip = strip

    def _execute(self, arg: Tag) -> str:
        """Extracts text from `bs4.Tag`."""
        return arg.get_text(separator=self.separator, strip=self.strip)

    def __eq__(self, x: Any) -> bool:
        # equal only if separator and strip are the same
        if not isinstance(x, Text):
            return False

        return self.separator == x.separator and self.strip == x.strip

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(separator={self.separator}, strip={self.strip})"
        )


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

    def _execute(self, arg: Tag) -> Optional[str]:
        """
        Extracts href attribute from a BeautifulSoup Tag.
        If attribute is not present, returns None.
        """
        return arg.get_attribute_list("href")[0]

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

    def _execute(self, arg: Tag) -> Optional[Tag]:
        """Extracts parent of `bs4.Tag`."""
        return arg.parent

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return [self.execute(tag)]

    def __eq__(self, x: Any) -> bool:
        # equal only if both are instances of Parent
        return isinstance(x, Parent)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
