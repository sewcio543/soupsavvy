"""
Module with classes for tag selection based on CSS selectors.

Contains implementation of basic CSS pseudo-classes like
:only-child, :empty, :nth-child().

They can be used in combination with other SoupSelector objects
to create more complex tag selection conditions.
"""

from itertools import islice
from typing import Optional

import soupsieve as sv
from bs4 import Tag

from soupsavvy.exceptions import InvalidCSSSelector
from soupsavvy.selectors.base import SelectableCSS, SoupSelector
from soupsavvy.selectors.tag_utils import TagIterator


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

    def __init__(self, selector: str) -> None:
        try:
            self._compiled = sv.compile(selector)
        except sv.SelectorSyntaxError:
            raise InvalidCSSSelector(
                "CSS selector constructed from provided parameters "
                f"is not valid: {selector}"
            )
        self._selector = selector

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

    Parameters
    ----------
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

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

    In case of passing tag parameter, selector is `{tag}:only-child`.
    Otherwise, selector is `:only-child`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> OnlyChild().selector
    :only-child
    >>> OnlyChild("li").selector
    li:only-child

    If tag is specified, two conditions must be met:
    - Tag is the only child of its parent
    - Tag has the specified tag name

    For more information on the :only-child selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-child
    """

    def __init__(self, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:only-child")


class Empty(CSSSoupSelector):
    """
    Class to select tags that are empty, i.e., have no children.
    It uses the CSS selector `:empty`.

    Parameters
    ----------
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

    Example
    --------
    >>> <div class="widget"> ❌
    ...    <div class="menu"></div> ✔️
    ... </div>

    Tag is only selected if it is empty.

    In case of passing tag parameter, selector is `{tag}:empty`.
    Otherwise, selector is `:empty`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> Empty().selector
    :empty
    >>> Empty("ol").selector
    ol:empty

    If tag is specified, two conditions must be met:
    - Tag is empty
    - Tag has the specified tag name

    Notes
    --------
    Any text or whitespace inside the tag is consider as a child
    and makes the tag non-empty.

    Example
    --------
    >>> <div class="widget">Hello World</div> ❌
    >>> <div class="widget"> </div> ❌

    These tags are not empty and do not match the selector.

    For more information on the :empty selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:empty
    """

    def __init__(self, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:empty")


class FirstChild(CSSSoupSelector):
    """
    Class to select tags that are the first child of their parent.
    It uses the CSS selector `:first-child`.

    Parameters
    ----------
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

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

    In case of passing tag parameter, selector is `{tag}:first-child`.
    Otherwise, selector is `:first-child`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> FirstChild().selector
    :first-child
    >>> FirstChild("li").selector
    li:first-child

    If tag is specified, two conditions must be met:
    - Tag is the first child of its parent
    - Tag has the specified tag name

    Notes
    --------
    FirstChild object is essentially the same as NthChild("1").

    For more information on the :first-child selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:first-child
    """

    def __init__(self, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:first-child")


class LastChild(CSSSoupSelector):
    """
    Class to select tags that are the last child of their parent.
    It uses the CSS selector `:last-child`.

    Parameters
    ----------
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

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

    In case of passing tag parameter, selector is `{tag}:last-child`.
    Otherwise, selector is `:last-child`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> LastChild().selector
    :last-child
    >>> LastChild("div").selector
    div:last-child

    If tag is specified, two conditions must be met:
    - Tag is the last child of its parent
    - Tag has the specified tag name

    Notes
    --------
    LastChild object is essentially the same as NthLastChild("1").

    For more information on the :last-child selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:last-child
    """

    def __init__(self, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:last-child")


class NthChild(CSSSoupSelector):
    """
    Class to select tags that are the nth child of their parent.
    It uses the CSS selector `:nth-child(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the child to be selected. Can be a number or a formula.
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

    In case of passing tag parameter, selector is `{tag}:nth-child(n)`.
    Otherwise, selector is `:nth-child(n)`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> NthChild("2").selector
    :nth-child(2)
    >>> NthChild("2", "li").selector
    li:nth-child(2)
    >>> NthChild("2n+1").selector
    :nth-child(2n+1)
    >>> NthChild("odd", "div").selector
    div:nth-child(odd)

    If tag is specified, two conditions must be met:
    - Tag is the nth child of its parent
    - Tag has the specified tag name

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-child
    """

    def __init__(self, nth: str, /, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:nth-child({nth})")


class NthLastChild(CSSSoupSelector):
    """
    Class to select tags that are the nth last child of their parent.
    It uses the CSS selector `:nth-last-child(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the child to be selected. Can be a number or a formula.
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

    In case of passing tag parameter, selector is `{tag}:nth-last-child(n)`.
    Otherwise, selector is `:nth-last-child(n)`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> NthLastChild("2").selector
    :nth-last-child(2)
    >>> NthLastChild("2", "li").selector
    li:nth-last-child(2)
    >>> NthLastChild("2n+1").selector
    :nth-last-child(2n+1)
    >>> NthLastChild("odd", "div").selector
    div:nth-last-child(odd)

    If tag is specified, two conditions must be met:
    - Tag is the nth last child of its parent
    - Tag has the specified tag name

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-child
    """

    def __init__(self, nth: str, /, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:nth-last-child({nth})")


class FirstOfType(CSSSoupSelector):
    """
    Class to select tags that are the first of their type in their parent.
    It uses the CSS selector `:first-of-type`.

    Parameters
    ----------
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

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

    In case of passing tag parameter, selector is `{tag}:first-of-type`.
    Otherwise, selector is `:first-of-type`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> FirstOfType().selector
    :first-of-type
    >>> FirstOfType("div").selector
    div:first-of-type

    If tag is specified, two conditions must be met:
    - Tag is the first of its type in its parent
    - Tag has the specified tag name

    Notes
    --------
    If tag is not specified, the first tag of any type is selected, which in
    case of finding single tag is equivalent to FirstChild() results.

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:first-of-type
    """

    def __init__(self, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:first-of-type")


class LastOfType(CSSSoupSelector):
    """
    Class to select tags that are the last of their type in their parent.
    It uses the CSS selector `:last-of-type`.

    Parameters
    ----------
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

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

    In case of passing tag parameter, selector is `{tag}:last-of-type`.
    Otherwise, selector is `:last-of-type`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> LastOfType().selector
    :last-of-type
    >>> LastOfType("div").selector
    div:last-of-type

    If tag is specified, two conditions must be met:
    - Tag is the last of its type in its parent
    - Tag has the specified tag name

    Notes
    --------
    If tag is not specified, the first tag of any type is selected, which in
    case of finding single tag is the equivalent to LastChild() results.

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:last-of-type
    """

    def __init__(self, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:last-of-type")


class NthOfType(CSSSoupSelector):
    """
    Class to select tags that are the nth of their type in their parent.
    It uses the CSS selector `:nth-of-type(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the tag to be selected. Can be a number or a formula.
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

    In case of passing tag parameter, selector is `{tag}:nth-of-type(n)`.
    Otherwise, selector is `:nth-of-type(n)`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> NthOfType("2").selector
    :nth-of-type(2)
    >>> NthOfType("2", "li").selector
    li:nth-of-type(2)
    >>> NthOfType("2n+1").selector
    :nth-of-type(2n+1)
    >>> NthOfType("even", "div").selector
    div:nth-of-type(even)

    If tag is specified, two conditions must be met:
    - Tag is the nth of its type in its parent
    - Tag has the specified tag name

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-of-type
    """

    def __init__(self, nth: str, /, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:nth-of-type({nth})")


class NthLastOfType(CSSSoupSelector):
    """
    Class to select tags that are the nth last of their type in their parent.
    It uses the CSS selector `:nth-last-of-type(n)`.

    Parameters
    ----------
    nth : str, positional
        Number of the tag to be selected. Can be a number or a formula.
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

    In case of passing tag parameter, selector is `{tag}:nth-last-of-type(n)`.
    Otherwise, selector is `:nth-last-of-type(n)`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> NthLastOfType("2").selector
    :nth-last-of-type(2)
    >>> NthLastOfType("2", "li").selector
    li:nth-last-of-type(2)
    >>> NthLastOfType("2n+1").selector
    :nth-last-of-type(2n+1)
    >>> NthLastOfType("even", "div").selector
    div:nth-last-of-type(even)

    If tag is specified, two conditions must be met:
    - Tag is the nth last of its type in its parent
    - Tag has the specified tag name

    For more information on the formula, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-of-type
    """

    def __init__(self, nth: str, /, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:nth-last-of-type({nth})")


class OnlyOfType(CSSSoupSelector):
    """
    Class to select tags that are the only of their type in their parent.
    It uses the CSS selector `:only-of-type`.

    Parameters
    ----------
    tag : str, optional
        Tag to be selected. If None, any tag is selected.

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

    In case of passing tag parameter, selector is `{tag}:only-of-type`.
    Otherwise, selector is `:only-of-type`, which is equal to passing "*",
    css wildcard selector as an argument.

    Example
    --------
    >>> OnlyOfType().selector
    :only-of-type
    >>> OnlyOfType("div").selector
    div:only-of-type

    If tag is specified, two conditions must be met:
    - Tag is the only tag of its type in its parent
    - Tag has the specified tag name

    For more information on the :only-of-type selector, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-of-type
    """

    def __init__(self, tag: Optional[str] = None) -> None:
        super().__init__(f"{tag or ''}:only-of-type")


class CSS(CSSSoupSelector):
    """
    Soupsavvy wrapper for simple search with CSS selectors.
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

    def __init__(self, css: str) -> None:
        super().__init__(css)
