from __future__ import annotations

import json
import random
import string
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup, Tag

from . import namespace, settings


class BaseGenerator(ABC):
    _data = None

    @classmethod
    def load_data(cls) -> None:
        if cls._data is not None:
            return

        with open(namespace.SETUP_FILE, "r") as f:
            cls._data = json.load(f)

    def __init__(self, *args, **kwargs) -> None:
        self.load_data()

    @property
    def data(self) -> dict:
        return self._data or {}

    @abstractmethod
    def generate(self) -> str:
        raise NotImplementedError()

    def generate_tag(self) -> Tag:
        markup = self.generate()
        return BeautifulSoup(markup, namespace.PARSER)

    def _generate_unique_id(self) -> str:
        new_id = "".join(
            random.choices(
                string.ascii_letters + string.digits,
                k=settings.UNIQUE_ID_LENGTH,
            )
        )
        return new_id

    def __repr__(self):
        return str(self)


class BaseTagGenerator(BaseGenerator): ...
