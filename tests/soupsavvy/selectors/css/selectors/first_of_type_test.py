"""Module with unit tests for FirstOfType css tag selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.css.selectors import FirstOfType
from tests.soupsavvy.selectors.conftest import find_body_element, strip, to_bs


@pytest.mark.css
@pytest.mark.selector
class TestFirstOfType:
    """Class with unit tests for FirstOfType tag selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert FirstOfType().css == ":first-of-type"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div>1</div>
            <div></div>
            <a class="widget">2</a>
            <div>
                <p>3</p>
                <p class="widget"></p>
                <a>4</a>
            </div>
            <a href="widget"></a>
            <span><a>56</a><a></a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<p>3</p>"""),
            strip("""<a>4</a>"""),
            strip("""<span><a>56</a><a></a></span>"""),
            strip("""<a>56</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div>1</div>
            <div>Hello</div>
            <a class="widget">2</a>
            <span>3</span>
            <span><a>4</a><a></a></span>
            <a>Hello</a>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <span>1</span>
            <span><a>Not child</a><a></a></span>
            <div>2</div>
            <div>Hello</div>
            <a>3</a>
            <a class="widget"><p>Not child</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType()
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<span>1</span>""")

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>1</div>
            <div>Hello</div>
            <a class="widget">2</a>
            <span><a>3</a></span>
            <a>Hello</a>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType()
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<span><a>3</a></span>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div>1</div>
            <div></div>
            <a class="widget">2</a>
            <div>
                <p>3</p>
                <p class="widget"></p>
                <a>4</a>
            </div>
            <a href="widget"></a>
            <span><a>56</a><a></a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType()
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div>1</div>
            <div>Hello</div>
            <a class="widget">2</a>
            <span><a>3</a></span>
            <a>Hello</a>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType()
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
        ]
