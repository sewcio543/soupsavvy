"""
Module for combinators defined in css.

They they combine other selectors in a way that gives them a useful relationship
to each other and the location of content in the document.

Soupsavvy provides combinators that are used to combine multiple SelectableSoup
objects in a similar fashion to CSS combinators.

Classes
-------
ChildCombinator - equivalent of CSS child combinator (>)
NextSiblingCombinator - equivalent of CSS adjacent sibling combinator (+)
SubsequentSiblingCombinator - equivalent of CSS general sibling combinator (*)
DescentCombinator - equivalent of CSS descendant combinator (" ")
SelectorList - equivalent of CSS selector list (,) or :is() pseudo-class

Notes
-----
For more information on CSS combinators see:
https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/Selectors/Combinators
"""

from dataclasses import dataclass
from functools import reduce
from itertools import chain, product
from typing import Optional

from bs4 import Tag

from soupsavvy.tags.base import IterableSoup, SelectableSoup
from soupsavvy.tags.namespace import FindResult
from soupsavvy.tags.tag_utils import UniqueTag


@dataclass(init=False)
class ChildCombinator(SelectableSoup, IterableSoup):
    """
    Class representing a child combinator in CSS selectors.

    Example
    -------
    >>> ChildCombinator(ElementTag("div"), ElementTag("a"))

    matches all 'a' elements that are direct children of 'div' elements.

    Example
    -------
    >>> <div class="widget"><a>Hello World</a></div> ✔️
    >>> <div class="widget"><span></span><a>Hello World</a></div> ✔️
    >>> <span class="widget"><a>Hello World</a></span> ❌
    >>> <div class="menu"><span>Hello World</span></div> ❌

    Object can be created as well by using greater than operator '>'
    on two SelectableSoup objects.

    Example
    -------
    >>> ElementTag("div") > ElementTag("a")

    Which is equivalent to the first example.

    This is an equivalent of CSS child combinator, that matches elements
    that are direct children of a specified element.

    Example
    -------
    >>> div.widget > a { color: red; }

    which translated to soupsavvy would be:

    Example
    -------
    >>> ChildCombinator(
    ...     ElementTag("div", attributes=[AttributeTag("class", "widget")]),
    ...     ElementTag("a")
    ... )
    >>> ElementTag("div", attributes=[AttributeTag("class", "widget")]) > ElementTag("a")

    Notes
    -----
    For more information on child combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Child_combinator
    """

    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes ChildCombinator object with provided positional arguments as tags.
        At least two SelectableSoup objects are required to create ChildCombinator.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.
            At least two SelectableSoup objects are required to create ChildCombinator.

        Notes
        -----
        Object can be initialized with more than two SelectableSoup objects,
        which would be equal to chaining multiple child combinators.

        Example
        -------
        >>> div > a > span

        translates to soupsavvy would be:

        Example
        -------
        >>> ChildCombinator(ElementTag("div"), ElementTag("a"), ElementTag("span"))

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        elements = [tag]

        for i, step in enumerate(self.steps):
            # only first step follows recursive rule, the rest are not recursive
            # to match only direct children
            recursive_ = recursive if i == 0 else False

            elements = reduce(
                list.__add__,
                (step.find_all(element, recursive=recursive_) for element in elements),
            )

            # break if no elements were found in the step
            if not elements:
                break

        return elements[:limit]


@dataclass(init=False)
class NextSiblingCombinator(SelectableSoup, IterableSoup):
    """
    Class representing a next sibling combinator in CSS selectors.

    Example
    -------
    >>> NextSiblingCombinator(ElementTag("div"), ElementTag("a"))

    matches all 'a' elements that immediately follow 'div' elements,
    it means that both elements are children of the same parent element.

    Example
    -------
    >>> <div class="widget"></div><a>Hello World</a> ✔️
    >>> <div class="widget"><a>Hello World</a></div> ❌
    >>> <div class="widget"></div><span></span><a>Hello World</a> ❌

    Object can be created as well by using plus operator '+'
    on two SelectableSoup objects.

    Example
    -------
    >>> div + a { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> NextSiblingCombinator(ElementTag("div"), ElementTag("a"))
    >>> ElementTag("div") + ElementTag("a")

    Notes
    -----
    For more information on next sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Next-sibling_combinator

    This is also known as the adjacent sibling combinator.
    """

    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes SubsequentSiblingCombinator object with provided
        positional arguments as tags. At least two SelectableSoup object are required
        to create SubsequentSiblingCombinator.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.
            At least two SelectableSoup objects are required
            to create SubsequentSiblingCombinator.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:

        elements = [tag]

        for i, step in enumerate(self.steps):
            if i == 0:
                # only first step follows recursive rule
                elements = step.find_all(elements[0], recursive=recursive)
                continue

            matching = {
                UniqueTag(element)
                for tag in elements
                for element in step.find_all(tag.parent or tag, recursive=False)
            }

            next_siblings = [
                UniqueTag(tag.find_next_sibling()) for tag in elements  # type: ignore
            ]

            matches: list[UniqueTag] = []
            last_step = i + 1 == len(self.steps)

            for element in next_siblings:
                if element in matching and element not in matches:
                    matches.append(element)

                    if len(matches) == limit and last_step:
                        break

            elements = [element.tag for element in matches]

            # break if no elements were found in the step
            if not elements:
                break

        return elements


@dataclass(init=False)
class SubsequentSiblingCombinator(SelectableSoup, IterableSoup):
    """
    Class representing a subsequent sibling combinator in CSS selectors.
    Subsequent sibling combinator separates two selectors
    and matches all instances of the second element that follow the first element
    (not necessarily immediately) and share the same parent element.

    Example
    -------
    >>> SubsequentSiblingCombinator(ElementTag("div"), ElementTag("a"))

    matches all 'a' elements that follow 'div' elements.

    Example
    -------
    >>> <div class="widget"></div><a>Hello World</a> ✔️
    >>> <div class="widget"><span></span><a>Hello World</a></div> ✔️
    >>> <span class="widget"><a>Hello World</a></span> ❌
    >>> <a>Hello World</a><div class="menu"></div> ❌

    Object can be created as well by using multiplication operator '*'
    on two SelectableSoup objects, due to the lack of support for '~' operator
    between two operands.

    Example
    -------
    >>> div ~ a { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> ElementTag("div") * ElementTag("a")
    >>> SubsequentSiblingCombinator(ElementTag("div"), ElementTag("a"))

    Notes
    -----
    For more information on subsequent sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Subsequent-sibling_combinator

    This is also known as the general sibling combinator.
    """

    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes SubsequentSiblingCombinator object with provided
        positional arguments as tags. At least two SelectableSoup object are required
        to create SubsequentSiblingCombinator.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.
            At least two SelectableSoup objects are required
            to create SubsequentSiblingCombinator.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:

        elements = [tag]

        for i, step in enumerate(self.steps):
            if i == 0:
                # only first step follows recursive rule
                elements = step.find_all(elements[0], recursive=recursive)
                continue

            matching = {
                UniqueTag(element)
                for tag in elements
                for element in step.find_all(tag.parent or tag, recursive=False)
            }

            next_siblings = [
                UniqueTag(sibling)  # type: ignore
                for tag in elements
                for sibling in tag.find_next_siblings()
            ]

            matches: list[UniqueTag] = []
            last_step = i + 1 == len(self.steps)

            for element in next_siblings:
                if element in matching and element not in matches:
                    matches.append(element)

                    if len(matches) == limit and last_step:
                        break

            elements = [element.tag for element in matches]

            # break if no elements were found in the step
            if not elements:
                break

        return elements


@dataclass(init=False)
class DescendantCombinator(SelectableSoup, IterableSoup):
    """
    Class representing a descent combinator in CSS selectors.
    Descent combinator separates two selectors and matches all instances
    of the second element that are descendants of the first element.

    Two SelectableSoup objects are required to create DescentCombinator,
    but more can be provided as positional arguments, which binds them
    in a sequence of steps to match.

    Example
    -------
    >>> DescentCombinator(
    >>>     ElementTag("div", [AttributeTag(name="class", value="menu")]),
    >>>     ElementTag("a", [AttributeTag(name="href", value="google", re=True)])
    >>> )

    matches all descendants of 'div' element with 'menu' class attribute
    that are 'a' elements with href attribute containing 'google'.

    Example
    -------
    >>> <div class="menu"><a href="google.com"></a></div> ✔️
    >>> <div class="menu"><div><a href="google.com"></a></div></div> ✔️
    >>> <div class="menu"><a href="duckduckgo.com"></a></div> ❌
    >>> <div class="widget"><a href="google.com"></a></div> ❌
    >>> <a href="google.com"></a> ❌
    >>> <div class="widget"></div> ❌

    Object can be created as well by using right shift operator '>>'
    on two SelectableSoup objects.

    Example
    -------
    >>> div a { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> ElementTag("div") >> ElementTag("a")
    >>> DescentCombinator(ElementTag("div"), ElementTag("a"))

    Notes
    -----
    For more information on subsequent sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Descendant_combinator
    """

    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes DescentCombinator object with provided positional arguments as tags.
        At least two SelectableSoup object required to create DescentCombinator.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.
            At least two SelectableSoup objects are required to create DescentCombinator.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        elements = [tag]

        for i, step in enumerate(self.steps):
            # only first step follows recursive rule
            recursive_ = recursive if i == 0 else True

            elements = reduce(
                list.__add__,
                (step.find_all(element, recursive=recursive_) for element in elements),
            )
            # break if no elements were found in the step
            if not elements:
                break

        return elements[:limit]


@dataclass(init=False)
class SelectorList(SelectableSoup, IterableSoup):
    """
    Class representing a list of selectors in CSS,
    a selector list is a comma-separated list of selectors,
    that selects all the matching nodes.

    Class represents an Union of multiple soup selectors.
    Provides elements matching any of the selectors in an Union.

    At least two SelectableSoup objects are required to create SelectorList,
    but more can be provided as positional arguments.

    Example
    -------
    >>> SelectorList(
    >>>     ElementTag("a"),
    >>>     ElementTag("div", [AttributeTag(name="class", value="widget")])
    >>> )

    matches all elements that have "a" tag name OR 'class' attribute "widget".

    Example
    -------
    >>> <a>Hello World</a> ✔️
    >>> <div class="widget">Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌

    This is an equivalent of CSS comma selector (selector list) or :is() selector.

    Example
    -------
    >>> h1, h1 { color: red;}
    >>> :is(h1, h2) { color: red; }

    This example translated to soupsavvy would be:

    Example
    -------
    >>> SoupUnionTag(ElementTag("h1"), ElementTag("h2"))
    >>> ElementTag("h1") | ElementTag("h2")

    Object can be created as well by using bitwise OR operator '|'
    on two SelectableSoup objects.

    Example
    -------
    >>> ElementTag(tag="a") | ElementTag("div", [AttributeTag(name="class", value="widget")])

    Which is equivalent to the first example.

    Notes
    -----
    For more information on selector list see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Selector_list
    """

    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes SelectorList object with provided positional arguments as tags.
        At least two SelectableSoup objects are required to create SelectorList.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def _find(self, tag: Tag, recursive: bool = True) -> FindResult:
        # iterates all tags and returns first element that matches
        for _tag_ in self.steps:
            result = _tag_.find(tag, recursive=recursive)

            if result is not None:
                return result

        return None

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return reduce(
            list.__add__,
            (_tag_.find_all(tag, recursive=recursive) for _tag_ in self.steps),
        )[:limit]
