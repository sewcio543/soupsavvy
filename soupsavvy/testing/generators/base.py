from __future__ import annotations

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup, Tag

from . import namespace, settings
from .templates.templates import BaseTemplate


class BaseGenerator(ABC):
    _template: BaseTemplate = BaseTemplate()

    @property
    def template(self) -> BaseTemplate:
        return self._template

    @abstractmethod
    def generate(self) -> str:
        raise NotImplementedError()

    def generate_tag(self) -> Tag:
        markup = self.generate()
        return BeautifulSoup(markup, namespace.PARSER)

    def __repr__(self):
        return str(self)


class BaseTagGenerator(BaseGenerator): ...
