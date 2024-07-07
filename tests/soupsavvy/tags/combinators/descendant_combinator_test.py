"""Testing module for DescendantCombinator class."""

import pytest

from soupsavvy.tags.combinators import DescendantCombinator
from soupsavvy.tags.exceptions import NotSoupSelectorException, TagNotFoundException
from tests.soupsavvy.tags.conftest import (
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.soup
@pytest.mark.combinator
class TestDescendantCombinator:
    """Class for DescendantCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            DescendantCombinator(MockDivSelector(), "string")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            DescendantCombinator("string", MockDivSelector())  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns the first tag that matches selector."""
        text = """
            <a>Hello</a>
            <div><span>Hello</span></div>
            <span class="widget"><a>Hello</a></span>
            <a class="link"><div class="link"></div></a>
            <div>
                <div>
                    <a class="widget">1</a>
                    <span class="widget"></span>
                    <a>2</a>
                </div>
            </div>
        """
        bs = find_body_element(to_bs(text))

        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches selector in not strict mode.
        """
        text = """
            <a>Hello</a>
            <div><span>Hello</span></div>
            <span class="widget"><a>Hello</a></span>
            <a class="link"><div class="link"></div></a>
            <div>
                <span class="widget"></span>
                <img src="image.jpg">
            </div>
        """
        bs = to_bs(text)
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches selector in strict mode.
        """
        text = """
            <a>Hello</a>
            <div><span>Hello</span></div>
            <span class="widget"><a>Hello</a></span>
            <a class="link"><div class="link"></div></a>
            <div>
                <span class="widget"></span>
                <img src="image.jpg">
            </div>
        """
        bs = to_bs(text)
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches all selectors
        if there are multiple selectors are provided.
        """
        text = """
            <p>Hello World</p>
            <div>
                <p>Hello 1</p>
            </div>
            <div>
                <a><p>Hello 2</p></a>
            </div>
            <div>
                <a>
                    <div>
                        <p>Hello 3</p>
                        <h1>Hello 4</h1>
                    </div>
                </a>
            </div>
            <div>
                <a>
                    <div>
                        <h1>Hello 5</h1>
                        <a>1</a>
                        <p>Hello 6</p>
                        <span>
                            <a><span>2</span></a>
                        </span>
                    </div>
                </a>
            </div>
            <div>
                <span>
                    <a>
                        <div>
                            <h1>Hello 7</h1>
                            <a>3</a>
                        </div>
                    </a>
                </span>
            </div>
        """
        bs = to_bs(text)
        selector = DescendantCombinator(
            MockDivSelector(),
            MockLinkSelector(),
            MockDivSelector(),
            MockLinkSelector(),
        )
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><span>2</span></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_finds_all_tags_matching_selectors(self):
        """Tests if find_all method returns all tags that match selector."""
        text = """
            <a>Hello</a>
            <a class="link"><div class="link"></div></a>
            <span class="widget"><a>Hello</a></span>
            <div>
                <a class="widget">1</a>
                <span class="widget"></span>
                <a>2</a>
            </div>
            <div><span>Hello</span></div>
            <div>
                <img src="image.jpg">
                <a class="widget"><span>3</span></a>
                <span>
                    <div><a>4</a></div>
                </span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a>2</a>"""),
            strip("""<a class="widget"><span>3</span></a>"""),
            strip("""<a>4</a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector.
        """
        text = """
            <a>Hello</a>
            <div><span>Hello</span></div>
            <span class="widget"><a>Hello</a></span>
            <a class="link"><div class="link"></div></a>
            <div>
                <span class="widget"></span>
                <img src="image.jpg">
            </div>
        """
        bs = to_bs(text)
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <span>
                <div>
                    <a href="github">Not child</a>
                </div>
            </span>
            <div><p>Hello 3</p></div>
            <a class="github">Hello 2</a>
            <div>
                <span>
                    <a href="github">1</a>
                </span>
                <p>Hello</p>
                <a href="github">2</a>
            </div>
            <div>
                <a href="github">3</a>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a href="github">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <span>
                <div>
                    <a href="github">Not child</a>
                </div>
            </span>
            <div><p>Hello 3</p></div>
            <a class="github">Hello 2</a>
            <span>
                <div>
                    <a href="github">1</a>
                    <p>Hello</p>
                </div>
                <a href="github">Hello</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <span>
                <div>
                    <a href="github">Not child</a>
                </div>
            </span>
            <div><p>Hello 3</p></div>
            <a class="github">Hello 2</a>
            <span>
                <div>
                    <a href="github">1</a>
                    <p>Hello</p>
                </div>
                <a href="github">Hello</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <span>
                <div>
                    <a href="github">Not child</a>
                </div>
            </span>
            <div><p>Hello 3</p></div>
            <a class="github">Hello 2</a>
            <div>
                <a href="github">1</a>
                <p>Hello</p>
                <div>
                    <a href="github">2</a>
                </div>
            </div>
            <div>
                <span>
                    <a href="github"><span>3</span></a>
                </span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a href="github">2</a>"""),
            strip("""<a href="github"><span>3</span></a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <span>
                <div>
                    <a href="github">Not child</a>
                </div>
            </span>
            <div><p>Hello 3</p></div>
            <a class="github">Hello 2</a>
            <div>
                <div><p>Hello</p></div>
                <span>Hello</span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a>Hello</a>
            <a class="link"><div class="link"></div></a>
            <span class="widget"><a>Hello</a></span>
            <div>
                <a class="widget">1</a>
                <span class="widget"></span>
                <span><a>2</a></span>
            </div>
            <div><span>Hello</span></div>
            <div>
                <img src="image.jpg">
                <a class="widget"><span>3</span></a>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a>2</a>"""),
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
            <span>
                <div>
                    <a href="github">Not child</a>
                </div>
            </span>
            <div><p>Hello 3</p></div>
            <a class="github">Hello 2</a>
            <div>
                <a href="github">1</a>
                <p>Hello</p>
                <div>
                    <a href="github">2</a>
                </div>
            </div>
            <div>
                <a href="github"><span>3</span></a>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a href="github">2</a>"""),
        ]

    def test_find_returns_none_if_first_step_was_not_found(self):
        """
        Tests if find returns None if the first step was not found.
        Ensures that combinators don't break when first step does not match anything.
        """
        text = """<a>First element</a>"""
        bs = to_bs(text)
        selector = DescendantCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []
