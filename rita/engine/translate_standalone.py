import logging
import re
import json

from functools import partial
from itertools import groupby, chain
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, TYPE_CHECKING, Mapping, Callable

from rita.utils import ExtendedOp
from rita.types import Rules, Patterns

logger = logging.getLogger(__name__)

ParseFn = Callable[[Any, "SessionConfig", ExtendedOp], str]


if TYPE_CHECKING:
    # We cannot simply import SessionConfig because of cyclic imports
    from rita.config import SessionConfig


def apply_operator(syntax, op: ExtendedOp) -> str:
    if op.empty():
        return syntax

    elif str(op) == "!":  # A bit complicated one
        return (r"((?!{})\w+)".format(syntax
                                      .rstrip(")")
                                      .lstrip("(")))
    else:
        return syntax + str(op)


def any_of_parse(lst, config: "SessionConfig", op: ExtendedOp) -> str:
    clause = r"((^|\s)(({0})\s?))".format("|".join(sorted(lst, key=lambda x: (-len(x), x))))
    return apply_operator(clause, op)


def regex_parse(r, config: "SessionConfig", op: ExtendedOp) -> str:
    if op.local_regex_override:
        return local_regex_parse(r, config, op)
    else:
        initial = "(" + r + r"\s?" + ")"
        return apply_operator(initial, op)


def local_regex_parse(r, config: "SessionConfig", op: ExtendedOp) -> str:
    if r[0] == "^" and r[-1] == "$":  # Fully strictly defined string?
        pattern = r[1:-1]
    elif r[0] == "^":  # We define start of the string
        pattern = r[1:] + r"\w*"
    elif r[-1] == "$":  # We define end of string
        pattern = r"\w*" + r[:-1]
    else:  # We define string inside word
        pattern = r"\w*" + r + r"\w*"

    initial = "(" + r"\b" + pattern + r"\b" + r"\s?" + ")"
    return apply_operator(initial, op)


def not_supported(key, *args, **kwargs) -> str:
    raise RuntimeError(
        "Rule '{0}' is not supported in standalone mode"
        .format(key)
    )


def person_parse(config: "SessionConfig", op: ExtendedOp) -> str:
    return apply_operator(r"([A-Z]\w+\s?)", op)


def entity_parse(value, config: "SessionConfig", op: ExtendedOp) -> str:
    if value == "PERSON":
        return person_parse(config, op=op)
    else:
        return not_supported(value)


def punct_parse(_, config: "SessionConfig", op: ExtendedOp) -> str:
    return apply_operator(r"([.,!;?:]\s?)", op)


def word_parse(value, config: "SessionConfig", op: ExtendedOp) -> str:
    initial = r"({}\s?)".format(value)
    return apply_operator(initial, op)


def fuzzy_parse(r, config: "SessionConfig", op: ExtendedOp) -> str:
    # TODO: build premutations
    return apply_operator(r"({0})[.,?;!]?".format("|".join(r)), op)


def phrase_parse(value, config: "SessionConfig", op: ExtendedOp) -> str:
    return apply_operator(r"({}\s?)".format(value), op)


def nested_parse(values, config: "SessionConfig", op: ExtendedOp) -> str:
    from rita.macros import resolve_value
    (_, patterns) = rules_to_patterns("", [resolve_value(v, config=config)
                                           for v in values], config=config)
    return r"(?P<g{}>{})".format(config.new_nested_group_id(), "".join(patterns))


def any_parse(_, config: "SessionConfig", op: ExtendedOp) -> str:
    return regex_parse(r".*", config, op)


PARSERS: Mapping[str, ParseFn] = {
    "any_of": any_of_parse,
    "any": any_parse,
    "value": word_parse,
    "regex": regex_parse,
    "entity": entity_parse,
    "lemma": partial(not_supported, "LEMMA"),
    "pos": partial(not_supported, "POS"),
    "punct": punct_parse,
    "fuzzy": fuzzy_parse,
    "phrase": phrase_parse,
    "nested": nested_parse,
}


def rules_to_patterns(label: str, data: Patterns, config: "SessionConfig"):
    logger.debug("data: {}".format(data))

    def gen():
        """
        Implicitly add spaces between rules
        """
        if len(data) == 0:
            return

        yield data[0]

        for (t, d, op) in data[1:]:
            yield t, d, op

    return (
        label,
        [PARSERS[t](d, config, op) for (t, d, op) in gen()],
    )


class RuleExecutor(object):
    def __init__(self, patterns, config, regex_impl=re, max_workers=4):
        self.config = config
        self.regex_impl = regex_impl
        self.patterns = [self.compile(label, rules)
                         for label, rules in patterns]
        self.raw_patterns = patterns
        self.max_workers = max_workers

    def compile(self, label, rules):
        flags = self.regex_impl.DOTALL
        if self.config.ignore_case:
            flags = flags | self.regex_impl.IGNORECASE

        indexed_rules = ["(?P<s{}>{})".format(i, r) if not r.startswith("(?P<") else r
                         for i, r in enumerate(rules)]
        regex_str = r"(?P<{0}>{1})".format(label, "".join(indexed_rules))
        try:
            return self.regex_impl.compile(regex_str, flags)
        except Exception as ex:
            logger.exception("Failed to compile: '{0}', Reason: \n{1}".format(regex_str, str(ex)))
            return None

    def _match_task(self, pattern, text, include_submatches):
        def gen():
            for match in pattern.finditer(text):
                def submatches():
                    for k, v in match.groupdict().items():
                        if not v or v.strip() == "":
                            continue
                        yield {
                            "key": k,
                            "text": v.strip(),
                            "start": match.start(k),
                            "end": match.end(k)
                        }

                yield {
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group().strip(),
                    "label": match.lastgroup,
                    "submatches": sorted(list(submatches()), key=lambda x: x["start"]) if include_submatches else []
                }
        return list(gen())

    def _results(self, text, include_submatches):
        with ThreadPoolExecutor(self.max_workers) as executor:
            tasks = [executor.submit(self._match_task, p, text, include_submatches)
                     for p in self.patterns]
            for future in as_completed(tasks):
                yield future.result(timeout=1)

    def execute(self, text, include_submatches=True):
        results = sorted(chain(*self._results(text, include_submatches)), key=lambda x: x["start"])
        for k, g in groupby(results, lambda x: x["start"]):
            group = list(g)
            if len(group) == 1:
                yield group[0]
            else:
                data = sorted(group, key=lambda x: -x["end"])
                yield data[0]

    @staticmethod
    def load(path, regex_impl=re):
        from rita.config import SessionConfig
        config = SessionConfig()
        with open(path, "r") as f:
            patterns = [(obj["label"], obj["rules"])
                        for obj in map(json.loads, f.readlines())]
            return RuleExecutor(patterns, config, regex_impl=regex_impl)

    def save(self, path):
        with open(path, "w") as f:
            for pattern in self:
                f.write("{0}\n".format(json.dumps(pattern)))

    def __iter__(self):
        for label, rules in self.raw_patterns:
            yield {"label": label, "rules": rules}


def compile_rules(rules: Rules, config: "SessionConfig", regex_impl=re, **kwargs) -> RuleExecutor:
    logger.info("Using standalone rule implementation")
    patterns = [rules_to_patterns(*group, config=config) for group in rules]
    executor = RuleExecutor(patterns, config, regex_impl=regex_impl)
    return executor
