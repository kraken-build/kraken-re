import pytest

from kraken.re.address import Address, CommonAddressSpec


def test__CommonAddressSpec__of() -> None:
    assert CommonAddressSpec.of(":foo") == CommonAddressSpec(None, "foo")
    assert CommonAddressSpec.of("/:foo") == CommonAddressSpec("/", "foo")
    assert CommonAddressSpec.of("/bar") == CommonAddressSpec("/bar", None)
    assert CommonAddressSpec.of("foo/bar:") == CommonAddressSpec("foo/bar", None)
    assert CommonAddressSpec.of(":") == CommonAddressSpec(None, None)


def test__CommonAddressSpec__matches_anything() -> None:
    assert CommonAddressSpec.of(":").matches_address(Address(".", "foo"))
    assert CommonAddressSpec.of(":").matches_address(Address("src", "spam"))


def test__CommonAddressSpec__matches_any_directory() -> None:
    assert CommonAddressSpec.of(":foo").matches_address(Address(".", "foo"))
    assert not CommonAddressSpec.of(":foo").matches_address(Address(".", "bar"))
    assert CommonAddressSpec.of(":foo").matches_address(Address("src", "foo"))
    assert not CommonAddressSpec.of(":foo").matches_address(Address("src", "bar"))


def test__CommonAddressSpec__matches_exact_directory() -> None:
    assert CommonAddressSpec.of("./:foo").matches_address(Address("./", "foo"))
    assert CommonAddressSpec.of("./:foo").matches_address(Address(".", "foo"))
    assert not CommonAddressSpec.of("./:foo").matches_address(Address("bar", "foo"))

    assert CommonAddressSpec.of("src:foo").matches_address(Address("src", "foo"))
    assert CommonAddressSpec.of("src:foo").matches_address(Address("./src", "foo"))
    assert not CommonAddressSpec.of("src:foo").matches_address(Address("./tests", "foo"))


def test__CommonAddressSpec__of__invalid() -> None:
    with pytest.raises(ValueError):
        CommonAddressSpec.of("")
    with pytest.raises(ValueError):
        CommonAddressSpec.of("foo/bar::bar")
