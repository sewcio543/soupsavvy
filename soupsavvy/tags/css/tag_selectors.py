from abc import abstractmethod
from typing import Iterable, Optional

from bs4 import Tag

from soupsavvy.tags.base import SelectableCSS, SelectableSoup
from soupsavvy.tags.namespace import FindResult
from soupsavvy.tags.tag_utils import TagIterator


class ConditionalSoup(SelectableSoup, SelectableCSS):

    @abstractmethod
    def _condition(self, tag: Tag) -> bool:
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    def _get_iterator(self, tag: Tag, recursive: bool) -> Iterable[Tag]:
        return TagIterator(tag, recursive=recursive)

    def _find(self, tag: Tag, recursive: bool = True) -> FindResult:
        iterator = self._get_iterator(tag, recursive=recursive)

        for _tag_ in iterator:
            if self._condition(_tag_):
                return _tag_

        return None

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        iterator = self._get_iterator(tag, recursive=recursive)
        return [_tag_ for _tag_ in iterator if self._condition(_tag_)][:limit]


class OnlyChild(ConditionalSoup):

    def _condition(self, tag: Tag) -> bool:
        return tag.find_next_sibling() is None and tag.find_previous_sibling() is None

    @property
    def selector(self) -> str:
        return ":only-child"


class EmptyTag(ConditionalSoup):

    def _condition(self, tag: Tag) -> bool:
        return len(tag.contents) == 0

    @property
    def selector(self) -> str:
        return ":empty"


class FirstChild(ConditionalSoup):

    def _condition(self, tag: Tag) -> bool:
        return tag.find_previous_sibling() is None

    @property
    def selector(self) -> str:
        return ":first-child"


class LastChild(ConditionalSoup):

    def _condition(self, tag: Tag) -> bool:
        return tag.find_next_sibling() is None

    @property
    def selector(self) -> str:
        return ":last-child"


class NthChild(ConditionalSoup):

    def __init__(self, n: int):
        self.n = n

    def _condition(self, tag: Tag) -> bool:
        return len(tag.find_previous_siblings()) == self.n - 1

    @property
    def selector(self) -> str:
        return f":nth-child({self.n})"


class NthLastChild(ConditionalSoup):

    def __init__(self, n: int):
        self.n = n

    def _condition(self, tag: Tag) -> bool:
        return len(tag.find_next_siblings()) == self.n - 1

    @property
    def selector(self) -> str:
        return f":nth-last-child({self.n})"


class FirstOfType(ConditionalSoup):

    def __init__(self, tag: str):
        self.tag = tag

    def _get_iterator(self, tag: Tag, recursive: bool) -> Iterable[Tag]:
        return tag.find_all(self.tag, recursive=recursive)

    def _condition(self, tag: Tag) -> bool:
        return len(tag.find_previous_siblings(self.tag)) == 0

    @property
    def selector(self) -> str:
        return f"{self.tag}:first-of-type"


class LastOfType(ConditionalSoup):

    def __init__(self, tag: str):
        self.tag = tag

    def _get_iterator(self, tag: Tag, recursive: bool) -> Iterable[Tag]:
        return tag.find_all(self.tag, recursive=recursive)

    def _condition(self, tag: Tag) -> bool:
        return len(tag.find_next_siblings(self.tag)) == 0

    @property
    def selector(self) -> str:
        return f"{self.tag}:last-of-type"


class NthOfType(ConditionalSoup):

    def __init__(self, tag: str, n: int):
        self.tag = tag
        self.n = n

    def _get_iterator(self, tag: Tag, recursive: bool) -> Iterable[Tag]:
        return tag.find_all(self.tag, recursive=recursive)

    def _condition(self, tag: Tag) -> bool:
        return len(tag.find_previous_siblings(self.tag)) == self.n - 1

    @property
    def selector(self) -> str:
        return f"{self.tag}:nth-of-type({self.n})"


class NthLastOfType(ConditionalSoup):

    def __init__(self, tag: str, n: int):
        self.tag = tag
        self.n = n

    def _get_iterator(self, tag: Tag, recursive: bool) -> Iterable[Tag]:
        return tag.find_all(self.tag, recursive=recursive)

    def _condition(self, tag: Tag) -> bool:
        return len(tag.find_next_siblings(self.tag)) == self.n - 1

    @property
    def selector(self) -> str:
        return f"{self.tag}:nth-last-of-type({self.n})"


class OnlyOfType(ConditionalSoup):

    def __init__(self, tag: str):
        self.tag = tag

    def _get_iterator(self, tag: Tag, recursive: bool) -> Iterable[Tag]:
        return tag.find_all(self.tag, recursive=recursive)

    def _condition(self, tag: Tag) -> bool:
        return (
            len(tag.find_previous_siblings(self.tag) + tag.find_next_siblings(self.tag))
            == 0
        )

    @property
    def selector(self) -> str:
        return f"{self.tag}:only-of-type"
