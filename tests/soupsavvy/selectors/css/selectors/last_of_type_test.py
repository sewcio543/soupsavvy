"""Module with unit tests for LastOfType css tag selector."""

import pytest

from soupsavvy.selectors.css.selectors import LastOfType
from tests.soupsavvy.conftest import ToElement, strip


@pytest.mark.css
@pytest.mark.selector
@pytest.mark.skip_lxml
class TestLastOfType:
    """Class with unit tests for LastOfType tag selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert LastOfType().css == ":last-of-type"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(
        self,
        to_element: ToElement,
    ):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <a class="widget"></a>
            <div>
                <p>Hello</p>
                <p class="widget">1</p>
                <a>2</a>
            </div>
            <div>3</div>
            <a href="widget">4</a>
            <span><a></a><a>56</a></span>
        """
        bs = to_element(text)
        selector = LastOfType()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p class="widget">1</p>"""),
            strip("""<a>2</a>"""),
            strip("""<div>3</div>"""),
            strip("""<a href="widget">4</a>"""),
            strip("""<span><a></a><a>56</a></span>"""),
            strip("""<a>56</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <a>Hello</a>
            <div>Hello</div>
            <span><a></a><a>1</a></span>
            <span>2</span>
            <a class="widget">3</a>
            <div><p>45</p></div>
        """
        bs = to_element(text)
        selector = LastOfType()
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
            <div></div>
            <a>Hello</a>
            <div>Hello</div>
            <span><a></a><a>Not child</a></span>
            <span>1</span>
            <a class="widget">2</a>
            <div><p>3</p></div>
        """
        bs = to_element(text)
        selector = LastOfType()
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<span>1</span>""")

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div></div>
            <a>Hello</a>
            <span><a></a><a>No child</a></span>
            <span>1</span>
            <div>Hello</div>
            <a class="widget">2</a>
            <div><p>3</p></div>
        """
        bs = to_element(text)
        selector = LastOfType()
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<div><p>3</p></div>"""),
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
            <a class="widget"></a>
            <div>
                <p>Hello</p>
                <p class="widget">1</p>
            </div>
            <div>2</div>
            <a href="widget">3</a>
            <span><a></a><a>45</a></span>
        """
        bs = to_element(text)
        selector = LastOfType()
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p class="widget">1</p>"""),
            strip("""<div>2</div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div></div>
            <a>Hello</a>
            <span><a></a><a>No child</a></span>
            <span>1</span>
            <div>Hello</div>
            <a class="widget">2</a>
            <div><p>3</p></div>
        """
        bs = to_element(text)
        selector = LastOfType()
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<a class="widget">2</a>"""),
        ]
