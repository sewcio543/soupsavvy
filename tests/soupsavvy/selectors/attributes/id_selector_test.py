"""Testing module for IdSelector class."""

import re

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.attributes import IdSelector
from tests.soupsavvy.conftest import ToElement, strip

#! in these tests there are examples where multiple elements have the same id
#! this is not a valid html, but it is used for testing purposes


@pytest.mark.selector
class TestIdSelector:
    """Class for IdSelector unit test suite."""

    def test_find_returns_first_match_with_any_value(self, to_element: ToElement):
        """
        Tests if find returns first tag with id attribute,
        when no value is specified.
        """
        text = """
            <div href="widget"></div>
            <span></span>
            <div id=""></div>
            <div id="dog"></div>
        """
        bs = to_element(text)
        selector = IdSelector()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div id=""></div>""")

    def test_find_returns_first_match_with_specific_value(self, to_element: ToElement):
        """Tests if find returns first tag with id attribute with specific value."""
        # even though there should not be multiple elements with the same id
        text = """
            <div class="widget"></div>
            <span id="menu"></span>
            <a id="widget"></a>
            <div id="widget"></d>
        """
        bs = to_element(text)
        selector = IdSelector("widget")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a id="widget"></a>""")

    def test_find_returns_first_match_with_pattern(self, to_element: ToElement):
        """
        Tests if find returns first tag with id attribute that matches
        specified regex pattern
        """
        text = """
            <div id="menu widget 12"></div>
            <span id="widget"></span>
            <div href="widget 12"></div>
            <div id="widget 123"></div>
            <div id="widget 45"></div>
        """
        bs = to_element(text)
        selector = IdSelector(value=re.compile(r"^widget.?\d{1,3}$"))
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div id="widget 123"></div>""")

    def test_find_returns_none_if_no_match_and_strict_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = to_element(text)
        selector = IdSelector(value="widget")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(
        self, to_element: ToElement
    ):
        """
        Tests find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = to_element(text)
        selector = IdSelector(value="widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self, to_element: ToElement):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="widget"></div>
            <div id="widget">1</div>
            <span id=""></span>
            <div id="menu"></div>
            <a id="widget">2</a>
            <div>
                <a id="widget">3</a>
            </div>
            <span class="widget"></span>
            <div id="widget"><span>4</span></div>
            <div id="widget123"></div>
        """
        bs = to_element(text)
        selector = IdSelector(value="widget")

        result = selector.find_all(bs)
        excepted = [
            strip("""<div id="widget">1</div>"""),
            strip("""<a id="widget">2</a>"""),
            strip("""<a id="widget">3</a>"""),
            strip("""<div id="widget"><span>4</span></div>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self, to_element: ToElement):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="menu"></div>
            <div id="widget123"></div>
        """
        bs = to_element(text)
        selector = IdSelector(value="widget")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
            <a id="widget"></a>
            <div id="widget"></div>
        """
        bs = to_element(text)
        selector = IdSelector("widget")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a id="widget"></a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a id="widget">Not child</a>
            </div>
            <div href="widget"></div>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = to_element(text)
        selector = IdSelector("widget")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self, to_element: ToElement
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <a id="widget">Not child</a>
            </div>
            <div href="widget"></div>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = to_element(text)
        selector = IdSelector("widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns an empty list if no child element
        matches the selector and recursive is False.
        """
        text = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = to_element(text)
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a id="widget">1</a>
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
            <div id="widget">2</div>
            <span id=""></span>
            <div id="widget">3</div>
            <span class="widget"></span>
            <div id="widget"><span>4</span></div>
        """
        bs = to_element(text)
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget">1</a>"""),
            strip("""<div id="widget">2</div>"""),
            strip("""<div id="widget">3</div>"""),
            strip("""<div id="widget"><span>4</span></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a id="widget">1</a>
            <div href="widget"></div>
            <div>
                <a id="widget">2</a>
            </div>
            <div id="menu"></div>
            <div id="widget">3</div>
            <span id=""></span>
        """
        bs = to_element(text)
        selector = IdSelector("widget")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget">1</a>"""),
            strip("""<a id="widget">2</a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self, to_element: ToElement
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <a id="widget">1</a>
            <div href="widget"></div>
            <div>
                <a id="widget">Not child</a>
            </div>
            <div id="menu"></div>
            <div id="widget">2</div>
            <span id=""></span>
            <span id="widget">3</span>
        """
        bs = to_element(text)
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget">1</a>"""),
            strip("""<div id="widget">2</div>"""),
        ]
