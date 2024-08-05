"""Module with unit tests for LastOfType css tag selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.tags.css.tag_selectors import LastOfType
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css
@pytest.mark.selector
class TestLastOfType:
    """Class with unit tests for LastOfType tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert LastOfType().css == ":last-of-type"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert LastOfType("div").css == "div:last-of-type"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
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
        bs = find_body_element(to_bs(text))
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

    def test_find_all_returns_all_tags_for_selector_with_tag_name(self):
        """Tests if find_all method returns all tags for selector with tag name."""
        text = """
            <div>Hello</div>
            <a class="widget"></a>
            <div>
                <p>text</p>
                <div>
                    <span>Hello</span>
                    <a class="widget"></a>
                    <a>1</a>
                </div>
                <p class="LastOfType"></p>
                <a>Hello</a>
                <a><span>2</span></a>
            </div>
            <div></div>
            <a href="widget">3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = LastOfType("a")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><span>2</span></a>"""),
            strip("""<a href="widget">3</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <a>Hello</a>
            <div>Hello</div>
            <span><a></a><a>1</a></span>
            <span>Hello</span>
            <a class="widget">2</a>
            <div><a><p>3</p></a></div>
        """
        bs = to_bs(text)
        selector = LastOfType("a")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><p></p></span>
            <span>Hello</span>
        """
        bs = to_bs(text)
        selector = LastOfType("a")
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
            <span><p></p></span>
            <span>Hello</span>
        """
        bs = to_bs(text)
        selector = LastOfType("a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div>Hello</div>
            <span><p></p></span>
            <span>Hello</span>
        """
        bs = to_bs(text)
        selector = LastOfType("a")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div></div>
            <div>Hello</div>
            <span><a></a><a>Not child</a></span>
            <a>Hello</a>
            <span>Hello</span>
            <a class="widget">1</a>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = LastOfType("a")
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
            <span><a></a><a>Not child</a></span>
            <span>Hello</span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = LastOfType("a")
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
            <span><a></a><a>Not child</a></span>
            <span>Hello</span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = LastOfType("a")

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
            <span><a></a><a>Not child</a></span>
            <span>Hello</span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = LastOfType("a")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
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
        bs = find_body_element(to_bs(text))
        selector = LastOfType()
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<div><p>3</p></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
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
        bs = find_body_element(to_bs(text))
        selector = LastOfType()
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p class="widget">1</p>"""),
            strip("""<div>2</div>"""),
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
            <div></div>
            <a>Hello</a>
            <span><a></a><a>No child</a></span>
            <span>1</span>
            <div>Hello</div>
            <a class="widget">2</a>
            <div><p>3</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = LastOfType()
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<a class="widget">2</a>"""),
        ]
