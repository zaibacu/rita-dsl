from typing import Any, Mapping

opts = Mapping[Any, Any]
RuleData = tuple[str, list[Any], str]
Patterns = list[RuleData]
RuleGroup = tuple[str, Patterns]
Rules = list[RuleGroup]
