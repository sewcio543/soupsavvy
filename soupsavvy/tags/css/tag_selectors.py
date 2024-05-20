"""
Module with classes for tag selection based on CSS selectors.

Contains implementation of basic CSS pseudo-classes like
:only-child, :empty, :nth-child().

They can be used in combination with other SelectableSoup objects
to create more complex tag selection conditions.
"""

from dataclasses import dataclass
from typing import Iterable, Optional

import soupsieve as sv
from bs4 import Tag

from soupsavvy.tags.base import SelectableCSS, SelectableSoup
from soupsavvy.tags.css.exceptions import InvalidCSSSelector
from soupsavvy.tags.namespace import FindResult
from soupsavvy.tags.tag_utils import TagIterator


class CSSSelectorSoup(SelectableSoup, SelectableCSS):
    """
    Base class for CSS selector based tag selection.
    Classes that base their selection on CSS selectors should inherit from this class
    and implement the `selector` property.

    By default, the `find` methods are implemented using the soupsieve library
    to match the selector.

    CSSSelectorSoup objects are based on SelectableSoup interface
    and can be easily used in combination with other SelectableSoup objects.
    """

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        iterator = self._get_iterator(tag, recursive=recursive)
        return [_tag_ for _tag_ in iterator if self._condition(_tag_)][:limit]

    def _find(self, tag: Tag, recursive: bool = True) -> FindResult:
        iterator = self._get_iterator(tag, recursive=recursive)

        for _tag_ in iterator:
            if self._condition(_tag_):
                return _tag_

        return None

    def _condition(self, tag: Tag) -> bool:
        """
        Condition based on which the tag is selected.
        By default, it uses the soupsieve library to match the selector.

        Parameters
        ----------
        tag : Tag
            Tag to be checked for selection.

        Returns
        -------
        bool
            True if the tag matches the selector, False otherwise.

        Raises
        ------
        InvalidCSSSelector
            If the css selector is not valid.
        """
        try:
            return sv.match(self.selector, tag)
        except sv.SelectorSyntaxError:
            raise InvalidCSSSelector(
                f"CSS selector constructed from provided parameters is not valid: {self.selector}"
            )

    def _get_iterator(self, tag: Tag, recursive: bool) -> Iterable[Tag]:
        """
        Returns an iterators over the tags to be checked for selection.

        Parameters
        ----------
        tag : Tag
            Tag to be iterated over.
        recursive : bool
            Whether to iterate recursively over the tag or just
            over the direct children.

        Returns
        -------
        Iterable[Tag]
            Iterator over the tags to be checked for selection.
        """
        return TagIterator(tag, recursive=recursive)


@dataclass
class OnlyChild(CSSSelectorSoup):
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

    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:only-child"


@dataclass
class Empty(CSSSelectorSoup):
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

    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:empty"


@dataclass
class FirstChild(CSSSelectorSoup):
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

    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:first-child"


@dataclass
class LastChild(CSSSelectorSoup):
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

    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:last-child"


@dataclass
class NthChild(CSSSelectorSoup):
    """
    Class to select tags that are the nth child of their parent.
    It uses the CSS selector `:nth-child(n)`.

    Parameters
    ----------
    n : str
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

    n: str
    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:nth-child({self.n})"


@dataclass
class NthLastChild(CSSSelectorSoup):
    """
    Class to select tags that are the nth last child of their parent.
    It uses the CSS selector `:nth-last-child(n)`.

    Parameters
    ----------
    n : str
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

    n: str
    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:nth-last-child({self.n})"


@dataclass
class FirstOfType(CSSSelectorSoup):
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

    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:first-of-type"


@dataclass
class LastOfType(CSSSelectorSoup):
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

    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:last-of-type"


@dataclass
class NthOfType(CSSSelectorSoup):
    """
    Class to select tags that are the nth of their type in their parent.
    It uses the CSS selector `:nth-of-type(n)`.

    Parameters
    ----------
    n : str
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

    n: str
    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:nth-of-type({self.n})"


@dataclass
class NthLastOfType(CSSSelectorSoup):
    """
    Class to select tags that are the nth last of their type in their parent.
    It uses the CSS selector `:nth-last-of-type(n)`.

    Parameters
    ----------
    n : str
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

    n: str
    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:nth-last-of-type({self.n})"


@dataclass
class OnlyOfType(CSSSelectorSoup):
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

    tag: Optional[str] = None

    @property
    def selector(self) -> str:
        tag = self.tag or ""
        return f"{tag}:only-of-type"
