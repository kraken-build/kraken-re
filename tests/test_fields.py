from typing import Any

import pytest

from kraken.re.address import Address
from kraken.re.exceptions import RequiredFieldMissingException
from kraken.re.fields import Field


def test__Field__abstract_subclass_can_be_required_without_defining_a_default_value() -> None:
    class MyField(Field[Any], abstract=True):

        pass


def test__Field__concrete_subclass_must_be_have_alias_and_be_required_or_have_default_value() -> None:
    class MyField1(Field[Any]):
        alias = "field1"
        required = True

    class MyField2(Field[Any]):
        alias = "field2"
        default = 42

    # Missing alias
    with pytest.raises(AssertionError):

        class MyField3(Field[Any]):
            default = 42

    # Missing default value
    with pytest.raises(AssertionError):

        class MyField4(Field[Any]):
            alias = "field4"


def test__Field__converts_None_to_default() -> None:
    class MyField(Field[Any]):
        alias = "field"
        default = "foo"

    assert MyField(None, Address.of("test:a")).value == "foo"


def test__Field__raises_error_on_None_for_required_field() -> None:
    class MyField(Field[Any]):
        alias = "field"
        required = True

    with pytest.raises(RequiredFieldMissingException):
        MyField(None, Address.of("test:a"))
