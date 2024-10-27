"""
Module with classes for tag selection based on CSS selectors.

Contains implementation of basic CSS pseudo-classes like
`:only-child`, `:empty`, `:nth-child()`.

They can be used in combination with other `SoupSelector` objects
to create more complex search procedures.

Classes
-------
- OnlyChild
- Empty
- FirstChild
- LastChild
- NthChild
- NthLastChild
- FirstOfType
- LastOfType
- NthOfType
- NthLastOfType
- OnlyOfType
- CSS - wrapper for simple search with CSS selectors
"""

from typing import Optional

from soupsavvy.base import SelectableCSS, SoupSelector
from soupsavvy.interfaces import IElement
from soupsavvy.utils.selector_utils import TagIterator, TagResultSet


class CSSSoupSelector(SoupSelector, SelectableCSS):
    """
    Base class for selectors based on css selectors.
    Classes that base their selection on CSS selectors should inherit from this class
    and implement the `selector` property.

    By default, the `find` methods are implemented using the `soupsieve` library
    to match the selector.

    CSSSoupSelector objects inherit from `SoupSelector` and can be easily used
    in combination with other `SoupSelector` objects.
    """

    SELECTOR: str

    def __init__(self) -> None:
        selector = self.__class__.SELECTOR.format(*self._formats)
        self._selector = selector

    @property
    def _formats(self) -> list[str]:
        """
        Returns list of arguments to be used to format css selector string.
        """
        return []

    @property
    def css(self) -> str:
        return self._selector

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        api = tag.css(self._selector)
        selected = api.select(tag)
        iterator = TagIterator(tag, recursive=recursive)
        result = TagResultSet(list(iterator)) & TagResultSet(selected)
        return result.fetch(limit)

    def __eq__(self, other: object) -> bool:
        # we only care if selector is equal with current implementation
        return isinstance(other, CSSSoupSelector) and self.css == other.css


class OnlyChild(CSSSoupSelector):
    """
    Selector for finding elements, that do not have any siblings.
    Counterpart of the CSS selector `:only-child` pseudo-class.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ❌
    ...    <div class="menu">Hello World 2 </div> ❌
    ... </div>

    Notes
    --------
    For more information on the :only-child pseudo-class, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-child
    """

    SELECTOR = ":only-child"


class Empty(CSSSoupSelector):
    """
    Selector for finding empty elements, i.e., that have no children.
    Counterpart of the CSS selector `:empty` pseudo-class.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu"></div> ✔️
    ... </div>

    Any text node is considered as a child and makes the element non-empty.

    Example
    --------
    >>> <div class="widget">Hello World</div> ❌
    ... <div class="widget"> </div> ❌

    These elements are not empty and do not match the selector.

    Notes
    --------
    For more information on the :empty selector, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:empty
    """

    SELECTOR = ":empty"


class FirstChild(CSSSoupSelector):
    """
    Selector for finding elements, that are the first child of their parent.
    Counterpart of the CSS selector `:first-child` pseudo-class.

    Example
    --------
    >>> <div class="widget"> ✔️
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ...    <div class="menu">Hello World 2 </div> ❌
    ... </div>

    Notes
    --------
    `FirstChild` object is essentially the same as NthChild("1").

    For more information on the :first-child selector, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:first-child
    """

    SELECTOR = ":first-child"


class LastChild(CSSSoupSelector):
    """
    Selector for finding elements, that are the last child of their parent.
    Counterpart of the CSS selector `:last-child` pseudo-class.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ✔️
    ...    <div class="menu">Hello World</div> ❌
    ...    <div class="menu">Hello World 2 </div> ✔️
    ... </div>

    Notes
    --------
    LastChild object is essentially the same as NthLastChild("1").
    Element that is the first and only child is matched as well.

    For more information on the :last-child selector, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:last-child
    """

    SELECTOR = ":last-child"


class NthBaseSelector(CSSSoupSelector):
    """Base class for selectors based on nth formula."""

    def __init__(self, nth: str) -> None:
        """
        Initialize the selector with the nth formula.

        Parameters
        ----------
        nth : str, positional
            Nth formula used to select the elements.
        """
        self._nth = nth
        super().__init__()

    @property
    def _formats(self) -> list[str]:
        return [self._nth]


class NthChild(NthBaseSelector):
    """
    Selector for finding elements, that are the nth child of their parent.
    Counterpart of the CSS selector `:nth-child(n)`.

    Example
    --------
    >>> NthChild("2").selector
    :nth-child(2)
    >>> NthChild("2n+1").selector
    :nth-child(2n+1)
    >>> NthChild("odd").selector
    :nth-child(odd)

    Notes
    --------
    For more information on the formula, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-child
    """

    SELECTOR = ":nth-child({})"


class NthLastChild(NthBaseSelector):
    """
    Selector for finding elements, that are the nth last child of their parent.
    Counterpart of the CSS selector `:nth-last-child(n)`.

    Example
    --------
    >>> NthLastChild("2").selector
    :nth-last-child(2)
    >>> NthLastChild("2n+1").selector
    :nth-last-child(2n+1)
    >>> NthLastChild("odd").selector
    :nth-last-child(odd)

    Notes
    --------
    For more information on the formula, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-child
    """

    SELECTOR = ":nth-last-child({})"


class FirstOfType(CSSSoupSelector):
    """
    Selector for finding elements, that are the first of their type in their parent.
    Counterpart of the CSS selector `:first-of-type` pseudo-class.

    Example
    --------
    >>> <div class="widget"> ✔️
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ...    <span class="menu">Hello World 2 </span> ✔️
    ...    <div class="menu">Hello World 3 </div> ❌
    ... </div>

    Notes
    --------
    For this selector the first tag of any type is selected, which in
    case of finding single tag is equivalent to `FirstChild` results.

    For more information on the formula, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:first-of-type
    """

    SELECTOR = ":first-of-type"


class LastOfType(CSSSoupSelector):
    """
    Selector for finding elements, that are the last of their type in their parent.
    Counterpart of the CSS selector `:last-of-type` pseudo-class.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ✔️
    ...    <div class="menu">Hello World</div> ❌
    ...    <span class="menu">Hello World 2 </span> ✔️
    ...    <div class="menu">Hello World 3 </div> ✔️
    ... </div>

    Notes
    --------
    For this selector the last tag of any type is selected, which in
    case of finding single tag is the equivalent to `LastChild` results.

    For more information on the formula, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:last-of-type
    """

    SELECTOR = ":last-of-type"


class NthOfType(NthBaseSelector):
    """
    Selector for finding elements, that are the nth of their type in their parent.
    Counterpart of the CSS selector `:nth-of-type(n)`.

    Example
    --------
    >>> NthOfType("2").selector
    :nth-of-type(2)
    >>> NthOfType("2n+1").selector
    :nth-of-type(2n+1)
    >>> NthOfType("even").selector
    :nth-of-type(even)

    Notes
    --------
    For more information on the formula, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-of-type
    """

    SELECTOR = ":nth-of-type({})"


class NthLastOfType(NthBaseSelector):
    """
    Selector for finding elements, that are the nth last of their type in their parent.
    Counterpart of the CSS selector `:nth-last-of-type(n)`.

    Example
    --------
    >>> NthLastOfType("2").selector
    :nth-last-of-type(2)
    >>> NthLastOfType("2n+1").selector
    :nth-last-of-type(2n+1)
    >>> NthLastOfType("even").selector
    :nth-last-of-type(even)

    Notes
    --------
    For more information on the formula, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-of-type
    """

    SELECTOR = ":nth-last-of-type({})"


class OnlyOfType(CSSSoupSelector):
    """
    Selector for finding elements, that don't have siblings of the same type.
    Counterpart of the CSS selector `:only-of-type` pseudo-class.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ...    <span class="menu">Hello World 2 </span> ❌
    ...    <span class="menu">Hello World 3 </span> ❌
    ... </div>
    ... <a class="widget"></a> ✔️

    Notes
    --------
    For more information on the :only-of-type selector, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-of-type
    """

    SELECTOR = ":only-of-type"


class CSS(CSSSoupSelector):
    """
    Selector for finding elements based on any provided CSS selector.
    `soupsieve` adapter, that allows any supported css selector
    to be used with other `soupsavvy` components.

    Example
    --------
    >>> CSS("div.menu")

    Would match:

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="menu_main"> ❌
    ...    <a class="menu">Hello World</a> ❌
    ... </div>
    ... <div class="menu"></div> ✔️

    Notes
    --------
    `CSS` component extends `bs4.Tag.select` implementation
    by adding non recursive search option.
    """

    SELECTOR = "{}"

    def __init__(self, css: str) -> None:
        """
        Initializes the selector with the provided css selector.

        Parameters
        ----------
        css : str
            CSS selector to be used for selecting elements.
        """
        self._css = css
        super().__init__()

    @property
    def _formats(self) -> list[str]:
        return [self._css]
