from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kraken.re.address import Address
from kraken.re.util.repr import SafeStr

if TYPE_CHECKING:
    from kraken.re.fields import Field
    from kraken.re.target import Target


class NoSuchFieldException(SafeStr, Exception):
    def __init__(self, target: Target, field_type: type[Field[Any]]) -> None:
        self.target = target
        self.field_type = field_type

    def __safe_str__(self) -> str:
        return f"target `{self.target.address}` of type `{self.target.alias}` has no field `{self.field_type.__name__}`"


class InvalidFieldException(Exception):
    pass


class InvalidFieldTypeException(InvalidFieldException):
    def __init__(self, address: Address, field_alias: str, raw_value: Any | None, expected_type: str) -> None:
        self.address = address
        self.field_alias = field_alias
        self.raw_value = raw_value
        self.expected_type = expected_type


class RequiredFieldMissingException(InvalidFieldException):
    def __init__(self, address: Address, field_name: str) -> None:
        self.address = address
        self.field_name = field_name

    def __str__(self) -> str:
        return f"{self.address}: `{self.field_name}`"


class InvalidTargetException(Exception):
    pass
