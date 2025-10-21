""" "Module with setup and mocks for testing BaseModel and its utilities."""

import pydantic
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

from soupsavvy.models.base import BaseModel
from tests.soupsavvy.conftest import (
    BaseMockOperation,
    MockClassWidgetSelector,
    MockDivSelector,
    MockIntOperation,
    MockLinkSelector,
    MockTextOperation,
)

SCOPE = MockDivSelector()
TITLE_SELECTOR = MockLinkSelector() | MockTextOperation()
PRICE_SELECTOR = MockClassWidgetSelector() | MockTextOperation() | MockIntOperation()


class MockModel(BaseModel):
    """
    Mock model for testing user-defined model, which is subclass of BaseModel.
    Simple model with two fields: title and price and div scope.
    """

    __scope__ = SCOPE

    title = TITLE_SELECTOR
    price = PRICE_SELECTOR


class MockTitle(BaseModel):
    """Mock model for testing migration with model as field."""

    __scope__ = MockLinkSelector()

    name = MockLinkSelector()


class MockAddress(BaseModel):
    """
    Mock model for testing migration with model as field.
    Used as redundant extra key in migration to test if it's ignored.
    """

    __scope__ = MockLinkSelector()

    street = MockLinkSelector()


class MockModelTitleField(BaseModel):
    """
    Mock model with field, which is instance of another model
    to test migration in such cases.
    """

    __scope__ = MockDivSelector()

    title = MockTitle
    price = PRICE_SELECTOR


class MockFrozenModel(BaseModel):
    """
    Mock model for testing frozen model instances.
    Setting attribute on them or computing hash.
    """

    __scope__ = MockDivSelector()
    __frozen__ = True

    title = TITLE_SELECTOR
    price = PRICE_SELECTOR


class MockMigrationTitle:
    """
    Mock class for testing migration of MockTitle model.
    This is target model, that instance of MockTitle, which is a field of model
    that is being migrated, should be migrated to.
    """

    def __init__(self, name, top: bool = True) -> None:
        """
        Initializes MockMigrationTitle with name and top attributes.
        Name is required, as it is field of MockTitle model.
        Top is optional, and is used for testing more complex migrations
        with additional attributes passed to model init.
        """
        self.name = name
        self.top = top

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.top == other.top


class MockMigrationName:
    """
    Mock class for testing migration of MockName model, which is a field of model,
    that is used as field of migrated model. Tests recursive behavior of migrate method.
    """

    def __init__(self, name: str) -> None:
        """Initializes MockMigrationName with name attribute."""
        self.name = name

    def __eq__(self, other) -> bool:
        return self.name == other.name


class MockNotEqualModel(BaseModel):
    """
    Mock model for testing model equality,
    if two instances of models are of different type,
    they are never equal, even if they have the same attributes.
    """

    __scope__ = SCOPE

    title = TITLE_SELECTOR
    price = PRICE_SELECTOR


class MockAllowEmptyTitle(BaseModel):
    """
    Mock model for testing case, when title can be empty and it's handled properly.
    """

    __scope__ = MockDivSelector()

    title = MockLinkSelector() | MockTextOperation(skip_none=True)
    price = PRICE_SELECTOR


class MockMigrationModel:
    """Mock class for testing migration to any custom model."""

    def __init__(self, title: str, price: int, **kwargs) -> None:
        self.title = title
        self.price = price

        for key, value in kwargs.items():
            setattr(self, key, value)

        if "error" in kwargs:
            raise ValueError("Forbidden key in kwargs")


class MockPydanticBook(pydantic.BaseModel):
    """Mock model for testing migration to Pydantic model."""

    title: str
    price: int


class Base(DeclarativeBase): ...


class MockSABook(Base):
    """Mock model for testing migration to SQLAlchemy model."""

    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    price = Column(Integer, nullable=True)


class MockModelOperation(BaseMockOperation):
    """Mock operation for testing operation on model."""

    def _execute(self, model: MockModel) -> str:
        return model.title.upper()  # type: ignore
