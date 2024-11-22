"""Module with unit tests for LastChild css selector."""

import pytest

from soupsavvy.selectors.css.selectors import LastChild
from tests.soupsavvy.conftest import ToElement, strip


@pytest.mark.css
@pytest.mark.selector
class TestLastChild:
    """Class with unit tests for LastChild selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert LastChild().css == ":last-child"

    def test_find_all_returns_all_matching_elements(
        self,
        to_element: ToElement,
    ):
        """Tests if find_all method returns all matching elements."""
        text = """
            <div></div>
            <div>
                <p></p>
                <p class="widget">1<a></a><a>2</a></p>
            </div>
            <span><a class="menu">34</a></span>
        """
        bs = to_element(text)
        selector = LastChild()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p class="widget">1<a></a><a>2</a></p>"""),
            strip("""<a>2</a>"""),
            strip("""<span><a class="menu">34</a></span>"""),
            strip("""<a class="menu">34</a>"""),
        ]

    def test_find_returns_first_element_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first element matching selector."""
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>1</a>
            </div>
            <span><a>2</a></span>
            <div><a>Hello</a><p>3</p></div>
            <a class="widget">4</a>
        """
        bs = to_element(text)
        selector = LastChild()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>Not child</a>
            </div>
            <span><a>Not child</a></span>
            <a class="widget">Hello</a>
            <a>1</a>
        """
        bs = to_element(text)
        selector = LastChild()
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>Not child</a>
            </div>
            <span><a>Not child</a></span>
            <a class="widget">Hello</a>
            <a>1</a>
        """
        bs = to_element(text)
        selector = LastChild()
        result = selector.find_all(bs, recursive=False)
        # at most one element can be returned
        assert list(map(lambda x: strip(str(x)), result)) == [strip("""<a>1</a>""")]

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>1</a>
            </div>
            <span><a>2</a></span>
            <div><a>Hello</a><p>3</p></div>
            <a class="widget">4</a>
        """
        bs = to_element(text)
        selector = LastChild()
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
        ]
