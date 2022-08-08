import pytest

from kraken.re.address import CommonAddressSpec


def test__CommonAddressSpec__of() -> None:
    assert CommonAddressSpec.of(":foo") == CommonAddressSpec(None, "foo")
    assert CommonAddressSpec.of("/:foo") == CommonAddressSpec("/", "foo")
    assert CommonAddressSpec.of("/bar") == CommonAddressSpec("/bar", None)
    assert CommonAddressSpec.of("foo/bar:") == CommonAddressSpec("foo/bar", None)
    assert CommonAddressSpec.of(":") == CommonAddressSpec(None, None)


def test__CommonAddressSpec__of__invalid() -> None:
    with pytest.raises(ValueError):
        CommonAddressSpec.of("")
    with pytest.raises(ValueError):
        CommonAddressSpec.of("foo/bar::bar")
