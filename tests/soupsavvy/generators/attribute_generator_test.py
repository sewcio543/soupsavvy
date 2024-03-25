"""Module for testing the AttributeGenerator class."""

import pytest
from bs4 import BeautifulSoup
from pytest import MonkeyPatch

from soupsavvy.testing.generators import namespace, settings
from soupsavvy.testing.generators.generators import AttributeGenerator


@pytest.mark.generator
class TestAttributeGenerator:

    def _extract_value(self, attribute: str) -> str:
        """Helper method to extract the value from the generated string."""
        return attribute.replace('"', "").split("=")[1]

    @pytest.mark.parametrize(
        argnames="generator",
        argvalues=[
            AttributeGenerator(name="class", value="test"),
            AttributeGenerator(name="class", value=["test", "test2"]),
            AttributeGenerator(name="class"),
        ],
        ids=["string_value", "iterable_value", "no_value"],
    )
    def test_can_be_printed(self, generator: AttributeGenerator):
        """
        Tests that the generator can be printed. AttributeGenerator have str and repr
        dunder methods implemented. Tests check if they don't raise any exceptions.
        """
        str(generator)
        repr(generator)

    @pytest.mark.parametrize(
        "use_templates", [True, False], ids=["templates", "no_templates"]
    )
    def test_generates_exact_value_when_string_passed(
        self, monkeypatch: MonkeyPatch, use_templates: bool
    ):
        """
        Test that the generator returns the exact value along attribute name
        when a string is passed. This should work regardless of the value of
        the USE_TEMPLATES_VALUE setting.
        """
        monkeypatch.setattr(settings, "USE_TEMPLATES_VALUE", use_templates)

        generator = AttributeGenerator(name="class", value="test")
        actual = generator.generate()
        expected = 'class="test"'
        assert actual == expected

    @pytest.mark.parametrize(
        "use_templates", [True, False], ids=["templates", "no_templates"]
    )
    def test_selects_value_from_options_when_value_is_an_iterable(
        self, monkeypatch: MonkeyPatch, use_templates: bool
    ):
        """
        Test that the generator returns one of the values from the options
        when an iterable is passed. This should work regardless of the value of
        the USE_TEMPLATES_VALUE setting.
        """
        monkeypatch.setattr(settings, "USE_TEMPLATES_VALUE", use_templates)

        options = ["test", "test2"]
        generator = AttributeGenerator(name="class", value=options)
        actual = generator.generate()
        value = self._extract_value(actual)
        assert value in options

    def test_generates_one_of_templates_when_value_not_specified_and_use_templates_settings_is_true(
        self, monkeypatch: MonkeyPatch
    ):
        """
        Test that the generator returns one of the values from standard templates
        defined in setup json file. It is used only when the value is not specified
        and the USE_TEMPLATES_VALUE setting is True. Templates are only defined for
        certain attributes, testing for 'class' attribute to ensure that the generator
        is using the templates.
        """
        monkeypatch.setattr(settings, "USE_TEMPLATES_VALUE", True)

        generator = AttributeGenerator(name="class")
        actual = generator.generate()
        value = self._extract_value(actual)
        assert value in generator.data["class"]

    @pytest.mark.parametrize(
        "use_templates", [True, False], ids=["templates", "no_templates"]
    )
    def test_generates_random_value_when_name_not_in_templates(
        self, monkeypatch: MonkeyPatch, use_templates: bool
    ):
        """
        Test that the generator returns a random value when the attribute name
        is not defined in the templates. Testing for a custom attribute name
        'custom_attribute' to ensure that the generator is not using the templates,
        but generating a random value.
        """
        monkeypatch.setattr(settings, "USE_TEMPLATES_VALUE", use_templates)

        generator = AttributeGenerator(name="custom_attribute")
        actual = generator.generate()
        value = self._extract_value(actual)
        assert len(value) == settings.UNIQUE_ID_LENGTH

    def test_generates_random_value_when_value_not_specified_and_use_templates_settings_is_false(
        self, monkeypatch: MonkeyPatch
    ):
        """
        Test that the generator returns random value when the value is not specified
        and the USE_TEMPLATES_VALUE setting is False.
        Testing for expected string of length defined in the settings.
        """
        monkeypatch.setattr(settings, "USE_TEMPLATES_VALUE", False)

        generator = AttributeGenerator(name="class")
        actual = generator.generate()
        value = self._extract_value(actual)
        assert value not in generator.data["class"]
        assert len(value) == settings.UNIQUE_ID_LENGTH

    def test_generate_tag_correctly(self):
        """
        Test that the generator can generate a correct bs4 Tag
        with 'generate_tag' method. This Tag should be the same as generated string
        parsed by BeautifulSoup with defined parser.
        """
        generator = AttributeGenerator(name="class", value="test")
        actual = generator.generate_tag()
        expected = BeautifulSoup(generator.generate(), namespace.PARSER)
        assert actual == expected
