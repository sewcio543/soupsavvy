"""Module for testing utilities for tag selectors."""

from unittest.mock import patch

import pytest
from bs4 import Tag

from soupsavvy.tags.tag_utils import TagIterator, UniqueTag

from .conftest import find_body_element, strip, to_bs


@pytest.fixture(scope="module")
def mock_tag() -> Tag:
    """Fixture for creating a mock bs4.Tag."""
    text = """
        <div>
            <a class="link"></a>
            <div class="link">
                <a class="menu"></a>
                <a class="menu"></a>
            </div>
        </div>
        <span class="widget"></span>
    """
    return to_bs(text)


class TestUniqueTag:
    """Class with unit tests for UniqueTag class."""

    def test_hashes_tag_by_id(self, mock_tag: Tag) -> None:
        """Tests that UniqueTag hashes bs4.Tag by id."""
        tag = UniqueTag(mock_tag)
        assert hash(tag) == id(mock_tag)

    def test_is_equal_to_unique_tag_with_the_same_tag(self, mock_tag: Tag) -> None:
        """
        Tests that UniqueTag is equal to another UniqueTag object with the same bs4.Tag.
        """
        tag1 = UniqueTag(mock_tag)
        tag2 = UniqueTag(mock_tag)
        assert tag1 == tag2

    def test_is_not_equal_to_bs4_tag_it_wraps(self, mock_tag: Tag) -> None:
        """
        Tests that UniqueTag is not equal to bs4.Tag object it wraps
        as they have different hashes.
        """
        tag1 = UniqueTag(mock_tag)
        assert tag1 != mock_tag

    def test_different_tags_with_same_content_have_different_hash(self):
        """
        Tests that two bs4.Tag objects with the same content wrapped by UniqueTag
        have different hashes and can be stored in set as different objects.
        """
        text = """<div class="menu"></div>"""
        tag1 = UniqueTag(to_bs(text))
        tag2 = UniqueTag(to_bs(text))

        assert hash(tag1) != hash(tag2)
        assert len({tag1, tag2}) == 2

    def test_is_not_equal_to_other_bs4_tag(self, mock_tag: Tag) -> None:
        """
        Tests that UniqueTag is not equal to other bs4.Tag then the one it wraps.
        """
        tag1 = UniqueTag(mock_tag)
        assert tag1 != mock_tag.div

    @pytest.mark.parametrize(
        argnames="other",
        argvalues=[1, "string"],
        ids=["int", "str"],
    )
    def test_is_not_equal_to_not_unique_tag_instance(
        self, mock_tag: Tag, other
    ) -> None:
        """
        Tests that UniqueTag is not equal to other objects then UniqueTag.
        Testing for int and str.
        """
        tag1 = UniqueTag(mock_tag)
        assert tag1 != other


class TestTagIterator:
    """Class with unit tests for TagIterator class."""

    def test_iterates_correctly_over_descendants_by_default(self, mock_tag: Tag):
        """
        Tests that TagIterator iterates over descendants by default
        and returns all tags in order of appearance.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag)
        expected = [
            strip(
                """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
                """
            ),
            strip("""<a class="link"></a>"""),
            strip(
                """
                <div class="link">
                    <a class="menu"></a>
                    <a class="menu"></a>
                </div>
                """
            ),
            strip("""<a class="menu"></a>"""),
            strip("""<a class="menu"></a>"""),
            strip("""<span class="widget"></span>"""),
        ]
        assert [str(tag) for tag in tag_iterator] == expected

    def test_iterates_correctly_over_children_if_recursive_set_to_false(
        self, mock_tag: Tag
    ):
        """
        Tests that TagIterator iterates over children if recursive is set to False.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag, recursive=False)
        expected = [
            strip(
                """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
                """
            ),
            strip("""<span class="widget"></span>"""),
        ]
        assert [str(tag) for tag in tag_iterator] == expected

    def test_iterator_resets_when_called_again(self, mock_tag: Tag):
        """
        Tests that iterator resets when called again.
        Calling __iter__ method of TagIterator resets the iterator to the beginning.
        """
        tag = find_body_element(mock_tag)
        tag_iterator = TagIterator(tag)

        iter_ = iter(tag_iterator)
        # first tag
        expected = strip(
            """
                <div>
                    <a class="link"></a>
                    <div class="link">
                        <a class="menu"></a>
                        <a class="menu"></a>
                    </div>
                </div>
            """
        )
        assert str(next(iter_)) == expected

        iter_ = iter(tag_iterator)
        assert str(next(iter_)) == expected

    def test_iterates_over_no_elements_iterable(self, mock_tag: Tag):
        """
        Tests that TagIterator iterates over no elements if tag has no children.
        In this case expected result is an empty list.
        """
        # span element has no children
        tag = mock_tag.span
        tag_iterator = TagIterator(tag)  # type: ignore
        assert list(tag_iterator) == []

    def test_skips_elements_that_are_not_tags(self, mock_tag: Tag):
        """
        Tests that TagIterator skips all elements that are not bs4.Tag.
        Iterators over elements implemented in bs4.Tag contain strings, which need
        to be skipped.
        """

        class TagWrapper:
            def __init__(self, tag):
                self._tag = tag

            def __getattr__(self, attr):
                if attr == "descendants":
                    return iter(["string", "string2", 12])
                return getattr(self._tag, attr)

        tag = TagWrapper(mock_tag)
        tag_iterator = TagIterator(tag)  # type: ignore
        assert list(tag_iterator) == []
