"""Module with unit tests for FirstOfType css tag selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.css.selectors import FirstOfType
from tests.soupsavvy.selectors.conftest import find_body_element, strip, to_bs


@pytest.mark.css
@pytest.mark.selector
class TestFirstOfType:
    """Class with unit tests for FirstOfType tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert FirstOfType().css == ":first-of-type"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert FirstOfType("div").css == "div:first-of-type"

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

    def test_find_all_returns_all_tags_for_selector_with_tag_name(self):
        """Tests if find_all method returns all tags for selector with tag name."""
        text = """
            <div>Hello</div>
            <div></div>
            <a class="widget">1</a>
            <div>
                <p>text</p>
                <a><span>2</span></a>
                <div>
                    <span>Hello</span>
                    <a class="widget">3</a>
                    <a>Hello</a>
                </div>
                <p class="FirstOfType"></p>
                <a>Hello</a>
            </div>
            <a href="widget"></a>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType("a")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><span>2</span></a>"""),
            strip("""<a class="widget">3</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <div>Hello</div>
            <a class="widget">1</a>
            <span><a>2</a><a></a></span>
            <span>Hello</span>
            <a>Hello</a>
            <div><a><p>3</p></a></div>
        """
        bs = to_bs(text)
        selector = FirstOfType("a")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><p>Not child</p></span>
            <span>Hello</span>
        """
        bs = to_bs(text)
        selector = FirstOfType("a")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><p>Not child</p></span>
            <span>Hello</span>
        """
        bs = to_bs(text)
        selector = FirstOfType("a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div>Hello</div>
            <span><p>Not child</p></span>
            <span>Hello</span>
        """
        bs = to_bs(text)
        selector = FirstOfType("a")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><a>Not child</a><a></a></span>
            <a class="widget">1</a>
            <span>Hello</span>
            <a>Hello</a>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType("a")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><a>Not child</a><a></a></span>
            <span>Hello</span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType("a")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><a>Not child</a><a></a></span>
            <span>Hello</span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType("a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><a>Not child</a><a></a></span>
            <span>Hello</span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = FirstOfType("a")
        result = selector.find_all(bs, recursive=False)
        assert result == []

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
