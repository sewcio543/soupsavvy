from __future__ import annotations

import random
from typing import Iterable, Optional, Union

from . import namespace, settings
from .base import BaseGenerator, BaseTagGenerator

ATTRIBUTE_TYPE = Union[
    "AttributeGenerator", str, tuple[str, str], tuple[str, Iterable[str]]
]
CHILD_TYPE = Union["TagGenerator", str]


class AttributeGenerator(BaseGenerator):
    def __init__(self, name: str, value: Optional[Union[str, Iterable[str]]] = None):
        self.name = name
        self.value = value
        super().__init__()

    def generate(self):
        value = self.value

        if self.value is None:
            options = self.data.get(self.name, [])

            conditions = [settings.USE_TEMPLATES_VALUE, options]
            value = (
                random.choice(options)
                if all(conditions)
                else self._generate_unique_id()
            )

        elif not isinstance(self.value, str):
            value = random.choice(list(self.value))

        return f'{self.name}="{value}"'

    def __str__(self):
        value = "?" if self.value is None else self.value
        return f"{self.__class__.__name__} -> [{self.name}={value}]"


class TagGenerator(BaseTagGenerator):
    def __init__(
        self,
        name: str,
        attrs: Iterable[ATTRIBUTE_TYPE] = (),
        children: Iterable[CHILD_TYPE] = (),
        text: Optional[str] = None,
    ):
        if name in namespace.VOID_TAGS and children:
            raise ValueError(f"{name} is a void tag and cannot have children")

        self.name = name
        self.attrs = [self._parse_attribute(attr) for attr in attrs]

        if len(set(attr.name for attr in self.attrs)) != len(self.attrs):
            raise ValueError("Attributes names must be unique")

        self.text = text
        self.children = [
            child if isinstance(child, TagGenerator) else TagGenerator(child)
            for child in children
        ]
        super().__init__()

    def _parse_attribute(self, attr: ATTRIBUTE_TYPE) -> AttributeGenerator:
        if isinstance(attr, AttributeGenerator):
            return attr
        elif isinstance(attr, tuple):
            return AttributeGenerator(*attr)
        return AttributeGenerator(attr)

    def generate(self):
        attrs = " ".join(attr.generate() for attr in self.attrs)

        if settings.GENERATE_ATTRS and not attrs:
            number = sum(
                random.random() < settings.CHANCE for _ in range(settings.MAX_ATTRS)
            )
            names = random.sample(namespace.ALL_ATTRS, k=number)
            attrs = " ".join(AttributeGenerator(name).generate() for name in names)

        sep = " " if attrs else ""
        children = "".join(child.generate() for child in self.children)
        tag = f"<{self.name}{sep}{attrs}>"

        if self.name in namespace.VOID_TAGS:
            return tag

        text = self.text

        if self.text is None:
            options = self.data.get(namespace.TEXT, [])

            conditions = [
                settings.USE_TEMPLATES_TEXT,
                options,
                random.random() < settings.CHANCE,
            ]
            text = random.choice(options) if all(conditions) else ""

        return f"{tag}{text}{children}</{self.name}>"

    def __str__(self):
        children = " < ..." if self.children else ""
        attributes = ", ".join(str(attr) for attr in self.attrs) or "?"
        return f"{self.__class__.__name__} -> {self.name}[{attributes}]{children}"


class WildTagGenerator(BaseTagGenerator):
    def __init__(
        self,
        name: str,
        n_elements: int = namespace.DEFAULT_N_ELEMENTS,
        max_depth: int = namespace.DEFAULT_MAX_DEPTH,
    ) -> None:
        self.max_depth = max_depth
        self.name = name
        self.n_elements = n_elements
        self.tags = self._generate_children(level=0)

    def _generate_children(self, level: int) -> Iterable[TagGenerator]:
        stop_conditions = [
            # max depth of the element reached
            level == self.max_depth,
            # random chance to have no child elements
            random.random() < settings.NO_CHILD_CHANCE,
        ]
        if any(stop_conditions):
            return []

        names = random.choices(namespace.ALL_TAGS, k=self.n_elements)
        tags = [
            TagGenerator(
                name,
                children=(
                    []
                    if name in namespace.VOID_TAGS
                    else self._generate_children(level=level + 1)
                ),
            )
            for name in names
        ]
        return tags

    def generate(self) -> str:
        markup = "".join(tag.generate() for tag in self.tags)
        return markup


class RandomMarkupGenerator(BaseGenerator):
    def __init__(
        self,
        tags: Iterable[CHILD_TYPE] = (),
        n_elements: int = namespace.DEFAULT_N_ELEMENTS,
    ):
        self.tags = [
            tag if isinstance(tag, TagGenerator) else TagGenerator(tag) for tag in tags
        ]

        if settings.ONLY_DEFINED_TAGS and tags:
            return

        self.tags += [
            WildTagGenerator(random.choice(namespace.ALL_TAGS))
            for _ in range(n_elements)
        ]

    def generate(self) -> str:
        markup = "".join(tag.generate() for tag in self.tags)
        return markup
