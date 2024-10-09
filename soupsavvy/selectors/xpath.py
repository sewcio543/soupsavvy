"""
Selector for finding elements based on XPath.
`lxml` adapter, that allows any supported XPath expressions
to be used with other `soupsavvy` components.

XPath search is not natively supported by `bs4`, finding element is delegated
to `lxml` library, and corresponding `bs4` elements are selected.

Classes
-------
- XPathSelector
"""

from itertools import islice
from typing import Any, Optional, Union

from bs4 import Tag

try:
    from lxml import html
    from lxml.etree import XPath, XPathSyntaxError
    from lxml.html.soupparser import _convert_tree as to_lxml
except ImportError as e:
    raise ImportError(
        "`soupsavvy.selectors.xpath` requires `lxml` package to be installed."
    ) from e

import soupsavvy.exceptions as exc
from soupsavvy.base import SoupSelector
from soupsavvy.utils.selector_utils import TagIterator


class XPathSelector(SoupSelector):
    """
    Selector for finding elements based on XPath expressions
    based on `lxml` implementation.

    Examples
    --------
    >>> selector = XPathSelector("//p[@class='menu']")
    ... selector.find(soup)

    Examples
    --------
    >>> from lxml.etree import XPath
    ... selector = XPathSelector(XPath("//p[@class='menu']", smart_strings=False))
    ... selector.find(soup)

    Expressions targeting attributes or text content can be used,
    but results are reduced to matching `bs4` elements.

    Examples
    --------
    >>> selector = XPathSelector("//div//@href")
    ... selector.find(soup)
    """

    def __init__(self, xpath: Union[str, XPath]) -> None:
        """
        Initializes `XPathSelector` with a given XPath expression.

        Parameters
        ----------
        xpath : str | lxml.etree.XPath
            String representing of xpath expression or compiled `XPath` object.

        Raises
        ------
        InvalidXPathSelector
            If the provided XPath string cannot be compiled into `XPath` object.
        """
        if not isinstance(xpath, XPath):
            try:
                xpath = XPath(xpath)
            except XPathSyntaxError as e:
                raise exc.InvalidXPathSelector(f"Parsing XPath '{xpath}' failed") from e

        self.xpath = xpath

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        element: html.HtmlElement = to_lxml(tag, None)  # type: ignore
        matches = self.xpath(element)

        # this approach is possible due to DFS traversal
        # strongly based on assumption, that both iterators are in sync
        lxml_iterator = (
            element.iterdescendants(None) if recursive else element.iterchildren(None)
        )
        soup_iterator = TagIterator(tag, recursive=recursive)

        return list(
            islice(
                (
                    soup
                    for soup, element in zip(soup_iterator, lxml_iterator)
                    if element in matches
                ),
                limit,
            )
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, XPathSelector):
            return False
        return self.xpath == other.xpath
