from collections.abc import Mapping
from typing import Any

opts = Mapping[Any, Any]
RuleData = tuple[str, list[Any], str]
Rule = tuple[str, RuleData]
Rules = list[Rule]
