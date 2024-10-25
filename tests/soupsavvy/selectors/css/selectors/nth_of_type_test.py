"""Module with unit tests for NthOfType css tag selector."""

from itertools import chain

import pytest

from soupsavvy.exceptions import InvalidCSSSelector, TagNotFoundException
from soupsavvy.selectors.css.selectors import NthOfType
from tests.soupsavvy.conftest import find_body_element, strip, to_element


@pytest.mark.css
@pytest.mark.selector
class TestNthOfType:
    """Class with unit tests for NthOfType tag selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert NthOfType("2n").css == ":nth-of-type(2n)"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <a>Hello</a>
            <a class="widget">1</a>
            <div>2</div>
            <div>
                <p class="widget">Hello</p>
                <p><span></span><a>3</a></p>
                <a>Hello</a>
                <span><a></a><a>4</a></span>
            </div>
            <a>Hello</a>
            <a>5</a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType("2n")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<div>2</div>"""),
            strip("""<p><span></span><a>3</a></p>"""),
            strip("""<a>4</a>"""),
            strip("""<a>5</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <a>Hello</a>
            <a class="widget">1</a>
            <div>2</div>
            <div>
                <p><span></span><a>3</a></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a></a><a>4</a></span>
            </div>
            <a>Hello</a>
            <a>5</a>
        """
        bs = to_element(text)
        selector = NthOfType("2n")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div>
                <a></a>
                <p><a></a></p>
            </div>
            <p></p>
            <a></a>
        """
        bs = to_element(text)
        selector = NthOfType("2n")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div>
                <a></a>
                <p><a></a></p>
            </div>
            <p></p>
            <a></a>
        """
        bs = to_element(text)
        selector = NthOfType("2n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div>
                <a></a>
                <p><a></a></p>
            </div>
            <p></p>
            <a></a>
        """
        bs = to_element(text)
        selector = NthOfType("2n")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <p><span></span><a>3</a></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a></a><a>4</a></span>
            </div>
            <div>1</div>
            <a>Hello</a>
            <a class="widget">2</a>
            <div>Hello</div>
            <a>Hello</a>
            <a><p>3</p></a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType("2n")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a></a>
                <a>Not child</a>
            </div>
            <p></p>
            <a></a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType("2n")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <a></a>
                <a>Not child</a>
            </div>
            <p></p>
            <a></a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType("3n")

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
            <div>
                <a></a>
                <a>Not child</a>
            </div>
            <p></p>
            <a></a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType("3n")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>
                <p><span></span><a>3</a></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a></a><a>4</a></span>
            </div>
            <div>1</div>
            <a>Hello</a>
            <a class="widget">2</a>
            <div>Hello</div>
            <a>Hello</a>
            <a><p>3</p></a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType("2n")
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<a><p>3</p></a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <a>Hello</a>
            <a class="widget">1</a>
            <div>2</div>
            <div>
                <p class="widget">Hello</p>
                <p><span></span><a>3</a></p>
                <a>Hello</a>
                <span><a></a><a>4</a></span>
            </div>
            <a>Hello</a>
            <a>5</a>
        """
        bs = to_element(text)
        selector = NthOfType("2n")
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
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
            <div>
                <p><span></span><a>3</a></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a></a><a>4</a></span>
            </div>
            <div>1</div>
            <a>Hello</a>
            <a class="widget">2</a>
            <div>Hello</div>
            <a>Hello</a>
            <a><p>3</p></a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType("2n")
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
        ]

    def test_raises_exception_when_invalid_css_selector(self):
        """
        Tests if InvalidCSSSelector exception is raised in find methods,
        when invalid css selector is passed.
        """
        selector = NthOfType("2x+1")
        bs = to_element("<div></div>")

        with pytest.raises(InvalidCSSSelector):
            selector.find(bs)

        with pytest.raises(InvalidCSSSelector):
            selector.find_all(bs)

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [2, 4, 6]),
            ("2n+1", [1, 3, 5]),
            # ignores whitespaces
            ("  2n  + 1", [1, 3, 5]),
            ("-n+3", [1, 2, 3]),
            ("even", [2, 4, 6]),
            ("odd", [1, 3, 5]),
            ("3", [3]),
            ("-3n", []),
            ("-3n+10", [1, 4]),
        ],
    )
    def test_returns_elements_based_on_nth_selector(
        self, nth: str, expected: list[int]
    ):
        """
        Tests if find_all returns all elements with specified tag name
        matching various nth selectors.
        """
        text = """
            <p>text 1</p>
            <a>text 1</a>
            <p>text 2</p>
            <a>text 2</a>
            <p>text 3</p>
            <a>text 3</a>
            <p>text 4</p>
            <a>text 4</a>
            <p>text 5</p>
            <a>text 5</a>
            <p>text 6</p>
            <a>text 6</a>
        """
        bs = find_body_element(to_element(text))
        selector = NthOfType(nth)
        results = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), results)) == list(
            chain.from_iterable(
                [(f"""<p>text {i}</p>""", f"""<a>text {i}</a>""") for i in expected]
            )
        )
