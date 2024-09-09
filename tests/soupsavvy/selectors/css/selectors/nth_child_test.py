"""Module with unit tests for NthChild css tag selector."""

import pytest

from soupsavvy.exceptions import InvalidCSSSelector, TagNotFoundException
from soupsavvy.selectors.css.selectors import NthChild
from tests.soupsavvy.conftest import find_body_element, strip, to_bs


@pytest.mark.css
@pytest.mark.selector
class TestNthChild:
    """Class with unit tests for NthChild tag selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert NthChild("2n").css == ":nth-child(2n)"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <a class="widget">1</a>
            <div>
                <p>Hello</p>
                <p class="widget">2</p>
                <a>Hello</a>
                <span><a>3</a><p>4</p></span>
            </div>
            <div>5</div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<p class="widget">2</p>"""),
            strip("""<span><a>3</a><p>4</p></span>"""),
            strip("""<p>4</p>"""),
            strip("""<div>5</div>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <div>1</div>
            <div>
                <a></a>
                <p><a>2</a></p>
                <span></span>
            </div>
            <span>3</span>
            <a class="widget"></a>
            <div><a></a><p>45</p></div>
        """
        bs = to_bs(text)
        selector = NthChild("2n")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_bs(text)
        selector = NthChild("3n")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_bs(text)
        selector = NthChild("3n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_bs(text)
        selector = NthChild("3n")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <a></a>
                <p><a>Not child</a></p>
                <span></span>
            </div>
            <div>1</div>
            <div></div>
            <span>2</span>
            <a class="widget"></a>
            <div><a></a><p>34</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><p></p><a></a><p>Not child</p></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("3n")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div><p></p><a></a><p>Not child</p></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("3n")

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
            <div><p></p><a></a><p>Not child</p></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("3n")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>
                <a></a>
                <p><a>Not child</a></p>
                <span></span>
            </div>
            <div>1</div>
            <div></div>
            <span>2</span>
            <a class="widget"></a>
            <div><a>3</a><p>Not child</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<span>2</span>"""),
            strip("""<div><a>3</a><p>Not child</p></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <a class="widget">1</a>
            <div>
                <p>Hello</p>
                <p class="widget">2</p>
                <a>Hello</a>
                <span><a>3</a><p>4</p></span>
            </div>
            <div>5</div>
        """
        bs = to_bs(text)
        selector = NthChild("2n")
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<p class="widget">2</p>"""),
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
                <a></a>
                <p><a>Not child</a></p>
                <span></span>
            </div>
            <div>1</div>
            <div></div>
            <span>2</span>
            <a class="widget"></a>
            <div><a>3</a><p>Not child</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<span>2</span>"""),
        ]

    def test_init_raise_exception_with_invalid_selector(self):
        """
        Tests if init raise InvalidCSSSelector exception
        if invalid n parameter is passed into the selector.
        """
        with pytest.raises(InvalidCSSSelector):
            NthChild("2x+1")

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [2, 4, 6]),
            ("2n+1", [1, 3, 5]),
            # ignores whitespaces
            ("   2n +  1", [1, 3, 5]),
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
        """Tests if find_all returns all elements matching various nth selectors."""
        text = """
            <div class="widget">1</div>
            <a class="widget">2</a>
            <div class="widget">3</div>
            <a class="widget">4</a>
            <div class="widget">5</div>
            <a class="widget">6</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild(nth)
        results = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), results)) == [
            (
                f"""<a class="widget">{i}</a>"""
                if (i % 2) == 0
                else f"""<div class="widget">{i}</div>"""
            )
            for i in expected
        ]
