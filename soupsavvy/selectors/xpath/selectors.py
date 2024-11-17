"""
Selector for finding elements based on XPath,
that allows any supported XPath expressions
to be used with other `soupsavvy` components.

Classes
-------
- XPathSelector
"""

from typing import Any, Optional

from soupsavvy.base import SoupSelector
from soupsavvy.interfaces import IElement
from soupsavvy.utils.selector_utils import TagIterator, TagResultSet


class XPathSelector(SoupSelector):
    """
    Selector for finding elements based on XPath expressions.

    Examples
    --------
    >>> selector = XPathSelector("//p[@class='menu']")
    ... selector.find(soup)

    Examples
    --------
    >>> from lxml.etree import XPath
    ... selector = XPathSelector(XPath("//p[@class='menu']", smart_strings=False))
    ... selector.find(soup)

    Expressions must target elements, not attributes or text content.

    Examples
    --------
    >>> selector = XPathSelector("//div//@href")
    ... selector.find(soup)
    None

    Notes
    -----
    Equality check includes only xpath expression, as lxml `XPath` object
    does not implement more specific `__eq__` method.
    """

    def __init__(self, xpath: Any) -> None:
        """
        Initializes `XPathSelector` with a given XPath expression.

        Parameters
        ----------
        xpath : str | lxml.etree.XPath
            String representing of xpath expression or compiled `XPath` object.
            It needs to target elements, not attributes or text content.

        Raises
        ------
        InvalidXPathSelector
            If the provided XPath string cannot be compiled into `XPath` object.
        """
        self.xpath = xpath

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        api = tag.xpath(self.xpath)
        selected = api.select(tag)
        iterator = TagIterator(tag, recursive=recursive)
        result = TagResultSet(list(iterator)) & TagResultSet(selected)
        return result.fetch(limit)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, XPathSelector):
            return False

        return self.xpath == other.xpath

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.xpath!r})"
