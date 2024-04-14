"""Module for testing templates components for the generators module."""

import string

import pytest

from soupsavvy.testing.generators.templates.templates import (
    ChoiceTemplate,
    ConstantTemplate,
    EmptyTemplate,
    RandomTemplate,
)


@pytest.mark.template
class TestEmptyTemplate:
    """Component with unit tests for the EmptyTemplate class."""

    @property
    def template(self) -> EmptyTemplate:
        """Fixture for an instance of the EmptyTemplate class."""
        return EmptyTemplate()

    def test_generates_empty_string(self):
        """Test that the template always generates an empty string."""
        assert self.template.generate() == ""


@pytest.mark.template
class TestRandomTemplate:
    """Component with unit tests for the RandomTemplate class."""

    def test_generated_string_consist_of_letters_and_digits(self):
        """Test that the generated string consists only of letters and digits."""
        template = RandomTemplate()
        actual = template.generate()
        options = string.ascii_letters + string.digits
        assert all(char in options for char in actual)

    @pytest.mark.parametrize(
        argnames="length",
        argvalues=[5, 1],
        ids=["multiple", "one"],
    )
    def test_generate_string_of_specified_length(self, length):
        """
        Test that the generated string has the specified length.
        Minimum acceptable length is 1.
        """
        template = RandomTemplate(length=length)
        actual = template.generate()

        assert isinstance(actual, str)
        assert len(actual) == length

    @pytest.mark.parametrize(
        argnames="length",
        argvalues=["string", 2.4, 2.0],
        ids=["string", "float", "float_int"],
    )
    def test_raises_error_when_length_is_not_integer(self, length):
        """
        Test that TypeError is raised when length is not an integer.
        Input parameter must be integer to be valid for random.choices.
        """

        with pytest.raises(TypeError):
            RandomTemplate(length=length)

    @pytest.mark.parametrize(
        argnames="length",
        argvalues=[0, -1],
        ids=["zero", "negative"],
    )
    def test_raises_error_when_length_is_less_then_one(self, length: int):
        """
        Test that ValueError is raised when length is less than 1.
        It does not make sense to generate empty strings.
        """

        with pytest.raises(ValueError):
            RandomTemplate(length=length)

    def test_setting_seed_generates_same_string(self):
        """
        Test that the generation process is the same when seed is set.
        Two instances with the same seed should generate the same string.
        """
        template = RandomTemplate(seed=42)
        template2 = RandomTemplate(seed=42)
        assert template.generate() == template2.generate()


@pytest.mark.template
class TestConstantTemplate:
    """Component with unit tests for the ConstantTemplate class."""

    CONSTANT_VALUE = "test"

    @pytest.fixture(scope="class")
    def template(self) -> ConstantTemplate:
        """Fixture for an instance of the ConstantTemplate class."""
        return ConstantTemplate(self.CONSTANT_VALUE)

    def test_generates_constant_string(self, template: ConstantTemplate):
        """Test that the template always generates a constant string."""
        assert template.generate() == self.CONSTANT_VALUE

    @pytest.mark.parametrize(
        argnames="value",
        argvalues=[1, None],
        ids=["int", "none"],
    )
    def test_casts_value_to_string_if_not_string_passed(self, value):
        """Tests if the value is cast to string if not a string is passed."""
        template = ConstantTemplate(value)
        assert template.generate() == str(value)


@pytest.mark.template
class TestChoiceTemplate:
    """Component with unit tests for the ChoiceTemplate class."""

    CHOICES = ["a", "b", "c"]

    @pytest.fixture(scope="class")
    def template(self) -> ChoiceTemplate:
        """Fixture for an instance of the ChoiceTemplate class."""
        return ChoiceTemplate(self.CHOICES)

    def test_generates_string_from_choices(self, template: ChoiceTemplate):
        """Test that the template generates a string from the choices."""
        assert template.generate() in self.CHOICES

    @pytest.mark.parametrize(
        argnames="choices",
        argvalues=[("a", "b", "c"), "abc", {"a", "b", "c"}],
        ids=["tuple", "string", "set"],
    )
    def test_accepts_choices_of_different_iterable_types(self, choices):
        """
        Test that the template accepts choices of different iterable types.
        It can be any iterable, because it's converted to a list.
        """
        template = ChoiceTemplate(choices)
        # order might be different, so we check the set
        assert set(template.choices) == {"a", "b", "c"}

    def test_casts_choice_to_string_if_choices_contain_different_type(self):
        """
        Tests that the choice is cast to string after being chosen
        when the choices contain different types.
        """
        choices = [1, 2, 3]
        template = ChoiceTemplate(choices)  # type: ignore
        assert template.generate() in list(map(str, choices))

    def test_setting_seed_generates_same_string(self):
        """
        Test that the generation process is the same when seed is set.
        Two instances with the same seed should generate the same string.
        """
        template = ChoiceTemplate(self.CHOICES, seed=42)
        template2 = ChoiceTemplate(self.CHOICES, seed=42)
        assert template.generate() == template2.generate()

    def test_single_element_iterable_is_allowed_and_will_generate_this_value(self):
        """
        Test that single element iterable is allowed
        and template will generate this value.
        """
        template = ChoiceTemplate(["a"])
        assert template.generate() == "a"
