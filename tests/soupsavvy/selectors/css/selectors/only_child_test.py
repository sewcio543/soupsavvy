"""Module with unit tests for OnlyChild css selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.css.selectors import OnlyChild
from tests.soupsavvy.conftest import ToElement, strip


@pytest.mark.css
@pytest.mark.selector
class TestOnlyChild:
    """Class with unit tests for OnlyChild selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert OnlyChild().css == ":only-child"

    def test_find_all_returns_all_matching_elements(
        self,
        to_element: ToElement,
    ):
        """Tests if find_all method returns all matching elements."""
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><a></a></div>
            <span><a><p>3</p><p></p></a></span>
            <div>
                <span><a>3</a></span>
                <span></span>
            </div>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<a><p>3</p><p></p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_returns_first_element_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first element matching selector."""
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><a></a></div>
            <span><a><p>3</p><p></p></a></span>
            <div>
                <span><a>3</a></span>
                <span></span>
            </div>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<p>1</p>""")

    def test_find_returns_none_if_no_match_and_strict_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><p>Hello</p><a></a></span>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><p>Hello</p><a></a></span>
        """
        bs = to_element(text)
        selector = OnlyChild()

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self, to_element: ToElement):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><p>Hello</p><a></a></span>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div><a>Not child</a></div>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div><a>Not child</a></div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><a>Not child</a></div>
            <div></div>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div><a>Not child</a></div>
            <div></div>
        """
        bs = to_element(text)
        selector = OnlyChild()

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><a>Not child</a></div>
            <div></div>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div><a>Not child</a></div>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find_all(bs, recursive=False)
        # at most one element can be returned
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a>Not child</a></div>""")
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><a></a></div>
            <span><a><p>3</p><p></p></a></span>
            <div>
                <span><a>3</a></span>
                <span></span>
            </div>
        """
        bs = to_element(text)
        selector = OnlyChild()
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<a><p>3</p><p></p></a>"""),
        ]
