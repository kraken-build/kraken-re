from kraken.re.rules import Rule, RuleSet
from kraken.re.util.frozendict import FrozenDict


def test__Rule__of__parses_function_signature_correctly() -> None:
    def my_rule(a: int, b: str) -> float:
        ...

    assert Rule.of(my_rule) == Rule(my_rule.__qualname__, FrozenDict({"a": int, "b": str}), float, my_rule)


def test__Rule__of__evaluates_string_annotations() -> None:
    def my_rule(a: int, b: "str") -> float:
        ...

    assert Rule.of(my_rule) == Rule(my_rule.__qualname__, FrozenDict({"a": int, "b": str}), float, my_rule)


def test__RuleSet__get_rules_for_output_type() -> None:
    def rule1(a: int) -> str:
        ...

    def rule2(a: str) -> float:
        ...

    def rule3(a: float) -> float:
        ...

    rules = RuleSet()
    rules.add_rule(Rule.of(rule1))
    rules.add_rule(Rule.of(rule2))
    rules.add_rule(Rule.of(rule3))

    assert list(rules.get_rules_for_output_type(int)) == []
    assert list(rules.get_rules_for_output_type(str)) == [Rule.of(rule1)]
    assert list(rules.get_rules_for_output_type(float)) == [Rule.of(rule2), Rule.of(rule3)]
