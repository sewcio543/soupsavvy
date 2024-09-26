"""
Module with classes for tag selection based on CSS selectors.

Contains implementation of basic CSS pseudo-classes like
:only-child, :empty, :nth-child().

They can be used in combination with other SoupSelector objects
to create more complex tag selection conditions.

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

from itertools import islice
from typing import Optional

import soupsieve as sv
from bs4 import Tag

import soupsavvy.exceptions as exc
from soupsavvy.base import SelectableCSS, SoupSelector
from soupsavvy.utils.selector_utils import TagIterator


class CSSSoupSelector(SoupSelector, SelectableCSS):
    """
    Base class for CSS selector based tag selection.
    Classes that base their selection on CSS selectors should inherit from this class
    and implement the `selector` property.

    By default, the `find` methods are implemented using the soupsieve library
    to match the selector.

    CSSSoupSelector objects are based on SoupSelector interface
    and can be easily used in combination with other SoupSelector objects.
    """

    _SELECTOR: str

    def __init__(self) -> None:
        selector = self.__class__._SELECTOR.format(*self._formats)

        try:
            self._compiled = sv.compile(selector)
        except sv.SelectorSyntaxError:
            raise exc.InvalidCSSSelector(
                "CSS selector constructed from provided parameters "
                f"is not valid: {selector}"
            )
        self._selector = selector

    @property
    def _formats(self) -> list[str]:
        """
        List of arguments to be used to format css selector string of the selector.
        """
        return []

    @property
    def css(self) -> str:
        return self._selector

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:

        iterator = TagIterator(tag, recursive=recursive)
        return list(islice(filter(self._compiled.match, iterator), limit))

    def __eq__(self, other: object) -> bool:
        # we only care if selector is equal with current implementation
        return isinstance(other, CSSSoupSelector) and self.css == other.css


class OnlyChild(CSSSoupSelector):
    """
    Class to select tags that are the only child of their parent.
    It uses the CSS selector `:only-child`.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ❌
    ...    <div class="menu">Hello World 2 </div> ❌
    ... </div>

    Tag is only selected if it is the only child of its parent.

    Example
    --------
    >>> OnlyChild().selector
    :only-child

    For more information on the :only-child selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-child
    """

    _SELECTOR = ":only-child"


class Empty(CSSSoupSelector):
    """
    Class to select tags that are empty, i.e., have no children.
    It uses the CSS selector `:empty`.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu"></div> ✔️
    ... </div>

    Tag is only selected if it is empty.

    Example
    --------
    >>> Empty().selector
    :empty

    Notes
    --------
    Any text or whitespace inside the tag is consider as a child
    and makes the tag non-empty.

    Example
    --------
    >>> <div class="widget">Hello World</div> ❌
    ... <div class="widget"> </div> ❌

    These tags are not empty and do not match the selector.

    For more information on the :empty selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:empty
    """

    _SELECTOR = ":empty"


class FirstChild(CSSSoupSelector):
    """
    Class to select tags that are the first child of their parent.
    It uses the CSS selector `:first-child`.

    Example
    --------
    >>> <div class="widget"> ✔️
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ...    <div class="menu">Hello World 2 </div> ❌
    ... </div>

    Tag is only selected if it is the first child of its parent.

    Example
    --------
    >>> FirstChild().selector
    :first-child

    Notes
    --------
    FirstChild object is essentially the same as NthChild("1").

    For more information on the :first-child selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:first-child
    """

    _SELECTOR = ":first-child"


class LastChild(CSSSoupSelector):
    """
    Class to select tags that are the last child of their parent.
    It uses the CSS selector `:last-child`.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu">Hello World</div> ✔️
    ... </div>
    ... <div class="widget"> ✔️
    ...    <div class="menu">Hello World</div> ❌
    ...    <div class="menu">Hello World 2 </div> ✔️
    ... </div>

    Tag is only selected if it is the last child of its parent.
    Element that is the first and only child is matched as well.

    Example
    --------
    >>> LastChild().selector
    :last-child

    Notes
    --------
    LastChild object is essentially the same as NthLastChild("1").

    For more information on the :last-child selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:last-child
    """

    _SELECTOR = ":last-child"


class _NthBaseSelector(CSSSoupSelector):
    """Base class for selectors based on nth formula."""

    def __init__(self, nth: str) -> None:
        self._nth = nth
        super().__init__()

    @property
    def _formats(self) -> list[str]:
        return [self._nth]


class NthChild(_NthBaseSelector):
    """
    Class to select tags that are the nth child of their parent.
    It uses the CSS selector `:nth-child(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the child to be selected. Can be a number or a formula.

    Example
    --------
    >>> NthChild("2").selector
    :nth-child(2)
    >>> NthChild("2n+1").selector
    :nth-child(2n+1)
    >>> NthChild("odd").selector
    :nth-child(odd)

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-child
    """

    _SELECTOR = ":nth-child({})"


class NthLastChild(_NthBaseSelector):
    """
    Class to select tags that are the nth last child of their parent.
    It uses the CSS selector `:nth-last-child(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the child to be selected. Can be a number or a formula.

    Example
    --------
    >>> NthLastChild("2").selector
    :nth-last-child(2)
    >>> NthLastChild("2n+1").selector
    :nth-last-child(2n+1)
    >>> NthLastChild("odd").selector
    :nth-last-child(odd)

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-child
    """

    _SELECTOR = ":nth-last-child({})"


class FirstOfType(CSSSoupSelector):
    """
    Class to select tags that are the first of their type in their parent.
    It uses the CSS selector `:first-of-type`.

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

    Tag is only selected if it is the first of its type in its parent.

    Example
    --------
    >>> FirstOfType().selector
    :first-of-type

    Notes
    --------
    For this selector the first tag of any type is selected, which in
    case of finding single tag is equivalent to FirstChild() results.

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:first-of-type
    """

    _SELECTOR = ":first-of-type"


class LastOfType(CSSSoupSelector):
    """
    Class to select tags that are the last of their type in their parent.
    It uses the CSS selector `:last-of-type`.

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

    Tag is only selected if it is the last of its type in its parent.
    Element that is the first and only child is matched as well.

    Example
    --------
    >>> LastOfType().selector
    :last-of-type

    Notes
    --------
    For this selector the last tag of any type is selected, which in
    case of finding single tag is the equivalent to LastChild() results.

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:last-of-type
    """

    _SELECTOR = ":last-of-type"


class NthOfType(_NthBaseSelector):
    """
    Class to select tags that are the nth of their type in their parent.
    It uses the CSS selector `:nth-of-type(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the tag to be selected. Can be a number or a formula.

    Example
    --------
    >>> NthOfType("2").selector
    :nth-of-type(2)
    >>> NthOfType("2n+1").selector
    :nth-of-type(2n+1)
    >>> NthOfType("even").selector
    :nth-of-type(even)

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-of-type
    """

    _SELECTOR = ":nth-of-type({})"


class NthLastOfType(_NthBaseSelector):
    """
    Class to select tags that are the nth last of their type in their parent.
    It uses the CSS selector `:nth-last-of-type(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the tag to be selected. Can be a number or a formula.

    Example
    --------
    >>> NthLastOfType("2").selector
    :nth-last-of-type(2)
    >>> NthLastOfType("2n+1").selector
    :nth-last-of-type(2n+1)
    >>> NthLastOfType("even").selector
    :nth-last-of-type(even)

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-of-type
    """

    _SELECTOR = ":nth-last-of-type({})"


class OnlyOfType(CSSSoupSelector):
    """
    Class to select tags that are the only of their type in their parent.
    It uses the CSS selector `:only-of-type`.

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

    Tag is only selected if it is the only tag of its type in its parent.

    Example
    --------
    >>> OnlyOfType().selector
    :only-of-type

    For more information on the :only-of-type selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-of-type
    """

    _SELECTOR = ":only-of-type"


class CSS(CSSSoupSelector):
    """
    `soupsavvy` wrapper for simple search with CSS selectors.
    Uses soupsieve library to match the tag, based on the provided CSS selector.

    Extends bs4 Tag.select implementation by adding non recursive search option.
    Provided css selector might be any selector supported by soupsieve.

    Parameters
    ----------
    css : str
        CSS selector to be used for tag selection.

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
    """

    _SELECTOR = "{}"

    def __init__(self, css: str) -> None:
        self._css = css
        super().__init__()

    @property
    def _formats(self) -> list[str]:
        return [self._css]
