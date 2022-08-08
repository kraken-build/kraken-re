import pytest

from kraken.re.address import Address
from kraken.re.exceptions import (
    InvalidFieldTypeException,
    InvalidTargetException,
    NoSuchFieldException,
    RequiredFieldMissingException,
)
from kraken.re.fields import FloatField, IntField
from kraken.re.target import Target


def test__Target__init_subclass_collect_field_types_from_empty_class() -> None:
    class MyTarget(Target):
        alias = "mytarget"
        fields = ()

    assert MyTarget._field_types == {}


def test__Target__init_subclass_collect_field_types() -> None:
    class AField(IntField):
        alias = "a"
        required = True

    class BField(IntField):
        alias = "b"
        required = True

    class CField(FloatField):
        alias = "c"
        required = True

    class MyTarget(Target):
        alias = "mytarget"
        fields = (AField, BField, CField)

    assert MyTarget._field_types == {"a": AField, "b": BField, "c": CField}


def test__Target__init_subclass_errors_on_duplicate_alias() -> None:
    class A1Field(IntField):
        alias = "a"
        required = True

    class A2Field(IntField):
        alias = "a"
        required = True

    with pytest.raises(InvalidTargetException):

        class MyTarget(Target):
            alias = "mytarget"
            fields = (A1Field, A2Field)


def test__Target__init_subclass_errors_on_duplicate_field_type() -> None:
    class AField(IntField):
        alias = "a"
        required = True

    with pytest.raises(InvalidTargetException):

        class MyTarget(Target):
            alias = "mytarget"
            fields = (AField, AField)


def test__Target__can_construct_and_get_field() -> None:
    class AField(IntField):
        alias = "a"
        required = True

    class BField(IntField):
        alias = "b"
        default = 100

    class MyTarget(Target):
        alias = "mytarget"
        fields = (AField, BField)

    target = MyTarget({"a": 42, "b": None}, Address.of("test:a"))
    assert target[AField] == AField(42, target.address)
    assert target[AField].value == 42
    assert target[BField] == BField(None, target.address)
    assert target[BField].value == 100

    target = MyTarget({"a": 55}, Address.of("test:b"))
    assert target[AField] == AField(55, target.address)
    assert target[AField].value == 55

    with pytest.raises(NoSuchFieldException):
        target[BField]

    # Field a must be an integer
    with pytest.raises(InvalidFieldTypeException):
        MyTarget({"a": "foo"}, Address.of("test:c"))

    # Field a must be present
    with pytest.raises(RequiredFieldMissingException):
        MyTarget({}, Address.of("test:d"))
