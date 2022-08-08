from __future__ import annotations

import dataclasses
import inspect
from typing import Any, Callable, Collection, Iterator

from kraken.re.util.frozendict import FrozenDict


@dataclasses.dataclass
class Rule:
    """Represents a rule that can transform the input types into the output type."""

    name: str
    input_types: FrozenDict[str, type]
    output_type: type[type]
    function: Callable[..., Any]

    def __post_init__(self) -> None:
        assert isinstance(self.name, str)
        assert isinstance(self.input_types, FrozenDict)
        assert all(isinstance(v, type) for v in self.input_types.values())
        assert isinstance(self.output_type, type)
        assert callable(self.function)

    def __str__(self) -> str:
        signature = ", ".join(f"{k}: {v.__name__}" for k, v in self.input_types.items())
        return f"{self.name}({signature}) -> {self.output_type.__name__}"

    def __repr__(self) -> str:
        return f"Rule<{self}>"

    def matches_inputs(self, input_types: Collection[type]) -> bool:
        return all(t in input_types for t in self.input_types.values())

    def apply_to_inputs(self, inputs: dict[type, str]) -> Any:
        kwargs = {k: inputs[v] for k, v in self.input_types.items()}
        result = self.function(**kwargs)
        if not isinstance(result, self.output_type):
            raise RuntimeError(
                f"rule `{self.name}` must return object of type {self.output_type.__qualname__} but "
                f"actually returned {type(result).__qualname__}"
            )
        return result

    @classmethod
    def of(cls, function: Callable[..., Any]) -> "Rule":
        """Construct a Rule object from a function."""

        def _eval(annotation: Any) -> Any:
            if isinstance(annotation, str):
                return eval(annotation, function.__globals__)
            return annotation

        # NOTE: inspect.signature(eval_str) is available in 3.10+, so for compatibility we evaluate string
        #       annotations manually.
        signature = inspect.signature(function)
        signature = inspect.Signature(
            parameters=[
                inspect.Parameter(name, param.kind, default=param.default, annotation=_eval(param.annotation))
                for name, param in signature.parameters.items()
            ],
            return_annotation=_eval(signature.return_annotation),
        )

        if signature.return_annotation is signature.empty:
            raise ValueError(f"rule function `{function.__qualname__}` must have a return type annotation")
        if not isinstance(signature.return_annotation, type):
            raise ValueError(
                f"rule function `{function.__qualname__}` return type annotation must be a type "
                f"(got `{type(signature.return_annotation).__name__}`)"
            )

        required_types = {}
        for param_name, param in signature.parameters.items():
            if param.annotation is signature.empty:
                raise ValueError(
                    f"rule function `{function.__qualname__}` is missing a type annotation for parameter `{param_name}`"
                )
            if not isinstance(param.annotation, type):
                raise ValueError(
                    f"rule function `{function.__qualname__}` parameter `{param_name}` type annotation must be a type "
                    f"(got `{type(param.annotation).__name__}`)"
                )
            required_types[param_name] = param.annotation

        return cls(
            function.__qualname__,
            FrozenDict(required_types),
            signature.return_annotation,
            function,
        )


class RuleSet:
    """The RuleSet contains all rules that are defined in a session."""

    def __init__(self) -> None:
        self._rules: list[Rule] = []
        self._rules_by_output_type: dict[type, list[Rule]] = {}

    def add_rule(self, rule: Rule) -> None:
        assert isinstance(rule, Rule), type(rule).__qualname__
        self._rules.append(rule)

    def get_rules_for_output_type(self, output_type: type, respect_inheritance: bool = True) -> Iterator[Rule]:
        """Return the rules that produce the given output type.

        :param output_type:
        :param respect_inheritance: If enabled, take inheritance into account and also return rules that produce
            a subclass of the given *output_type*.
        """

        if not respect_inheritance:
            yield from self._rules_by_output_type.get(output_type, [])
            return

        for type_ in self._rules_by_output_type:
            if issubclass(type_, output_type):
                yield from self._rules_by_output_type[type_]
