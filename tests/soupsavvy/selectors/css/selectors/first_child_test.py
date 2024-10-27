"""Module with unit tests for FirstChild css tag selector."""

import pytest

from soupsavvy.selectors.css.selectors import FirstChild
from tests.soupsavvy.conftest import ToElement, strip


@pytest.mark.css
@pytest.mark.selector
class TestFirstChild:
    """Class with unit tests for FirstChild tag selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert FirstChild().css == ":first-child"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(
        self,
        to_element: ToElement,
    ):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div>1</div>
            <div></div>
            <div>
                <p>2</p>
                <p class="widget"></p>
            </div>
            <span><a class="menu">3</a></span>
        """
        bs = to_element(text)
        selector = FirstChild()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<p>2</p>"""),
            strip("""<a class="menu">3</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div>1</div>
            <div>
                <a><p>23</p></a>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><a>3</a><p></p</span>
            <a class="widget"></a>
        """
        bs = to_element(text)
        selector = FirstChild()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <a>1</a>
            <div></div>
            <div>
                <a>Not child</a>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><a>Not child</a></span>
        """
        bs = to_element(text)
        selector = FirstChild()
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
            <a>1</a>
            <div></div>
            <div>
                <a>Not child</a>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><a>Not child</a></span>
        """
        bs = to_element(text)
        selector = FirstChild()
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
            <div>1</div>
            <div>
                <a>2</a>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><a>3</a></span>
            <a class="widget"></a>
        """
        bs = to_element(text)
        selector = FirstChild()
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a>2</a>"""),
        ]
