from typing import Any, Mapping, Tuple, List, AnyStr

opts = Mapping[Any, Any]
RuleData = Tuple[AnyStr, List[Any], AnyStr]
Patterns = List[RuleData]
RuleGroup = Tuple[AnyStr, Patterns]
Rules = List[RuleGroup]
