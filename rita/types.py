from typing import Any, Mapping, Tuple, List

opts = Mapping[Any, Any]
RuleData = Tuple[str, Any, Any]
# Mid-pipeline a pattern list can hold RuleData tuples, plain lists and callables
Patterns = List[Any]
RuleGroup = Tuple[str, Patterns]
Rules = List[RuleGroup]
