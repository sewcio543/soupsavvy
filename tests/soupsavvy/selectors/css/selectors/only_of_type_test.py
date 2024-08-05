"""Module with unit tests for OnlyOfType css tag selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.css.selectors import OnlyOfType
from tests.soupsavvy.selectors.conftest import find_body_element, strip, to_bs


@pytest.mark.css
@pytest.mark.selector
class TestOnlyOfType:
    """Class with unit tests for OnlyOfType tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert OnlyOfType().css == ":only-of-type"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert OnlyOfType("div").css == "div:only-of-type"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><p></p></div>
            <span><p>2</p><p></p></span>
            <div>
                <span><a>3</a><p>4</p></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<span><p>2</p><p></p></span>"""),
            strip("""<a>3</a>"""),
            strip("""<p>4</p>"""),
        ]

    def test_find_all_returns_all_tags_for_selector_with_tag_name(self):
        """Tests if find_all method returns all tags for selector with tag name."""
        text = """
            <div></div>
            <p><a>1</a><a></a></p>
            <div><p>Hello</p><p></p></div>
            <span><p></p><p></p></span>
            <div>
                <span><a></a><p>2</p></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType("p")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p><a>1</a><a></a></p>"""),
            strip("""<p>2</p>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><p></p></div>
            <span><p>2</p><p></p></span>
            <div>
                <span><a>3</a><p>4</p></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<p>1</p>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div><p></p><p>Hello</p></div>
            <span><p>hello</p><p></p></span>
            <span>
                <span><a>Hello</a><a></a></span>
                <span></span>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div><p></p><p>Hello</p></div>
            <span><p>hello</p><p></p></span>
            <span>
                <span><a>Hello</a><a></a></span>
                <span></span>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div><p></p><p>Hello</p></div>
            <span><p>hello</p><p></p></span>
            <span>
                <span><a>Hello</a><a></a></span>
                <span></span>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div></div>
            <div><a>Not child</a><p>Not child</p></div>
            <span>1</span>
            <a><p>2</p></a>
            <div>Hello</div>
            <p>3</p>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<span>1</span>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div></div>
            <div><a>Not child</a><p>Not child</p></div>
            <span><a></a></span>
            <div>Hello</div>
            <span></span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div></div>
            <div><a>Not child</a><p>Not child</p></div>
            <span><a></a></span>
            <div>Hello</div>
            <span></span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()

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
            <div><a>Not child</a><p>Not child</p></div>
            <span><a></a></span>
            <div>Hello</div>
            <span></span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div></div>
            <div><a>Not child</a><p>Not child</p></div>
            <span>1</span>
            <a><p>2</p></a>
            <div>Hello</div>
            <p>3</p>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<p>3</p>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><p></p></div>
            <span><p>2</p><p></p></span>
            <div>
                <span><a>3</a><p>4</p></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<span><p>2</p><p></p></span>"""),
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
            <div><a>Not child</a><p>Not child</p></div>
            <span>1</span>
            <a><p>2</p></a>
            <div>Hello</div>
            <p>3</p>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyOfType()
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span>1</span>"""),
            strip("""<a><p>2</p></a>"""),
        ]
