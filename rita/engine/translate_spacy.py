import logging

from functools import partial
from typing import Any, TYPE_CHECKING, Mapping, Callable, Generator, AnyStr

from rita.utils import ExtendedOp
from rita.types import Rules, Patterns

logger = logging.getLogger(__name__)

SpacyPattern = Generator[Mapping[AnyStr, Any], None, None]
ParseFn = Callable[[Any, "SessionConfig", ExtendedOp], SpacyPattern]

if TYPE_CHECKING:
    # We cannot simply import SessionConfig because of cyclic imports
    from rita.config import SessionConfig


def any_of_parse(lst, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    if op.ignore_case(config):
        normalized = sorted([item.lower()
                             for item in lst])
        base = {"LOWER": {"IN": normalized}}
    else:
        base = {"LOWER": {"IN": sorted(lst)}}

    if not op.empty():
        base["OP"] = op.value
    yield base


def regex_parse(r, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    if op.ignore_case(config):
        d = {"LOWER": {"REGEX": r.lower()}}
    else:
        d = {"TEXT": {"REGEX": r}}

    if not op.empty():
        d["OP"] = op.value
    yield d


def fuzzy_parse(r, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    # TODO: build premutations
    d = {"LOWER": {"REGEX": "({0})[.,?;!]?".format("|".join(r))}}
    if not op.empty():
        d["OP"] = op.value
    yield d


def generic_parse(tag, value, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    d = {}
    if isinstance(value, list) and len(value) > 1:
        value = {"IN": value}

    d[tag] = value

    if not op.empty():
        d["OP"] = op.value
    yield d


def entity_parse(value, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    tag = "ENT_TYPE"
    if op.empty():
        op.op = "+"
    return generic_parse(tag, value, config, op)


def punct_parse(_, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    d = dict()
    d["IS_PUNCT"] = True
    if not op.empty():
        d["OP"] = op.value
    yield d


def any_parse(_, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    d = dict()
    if not op.empty():
        d["OP"] = op.value
    yield d


def phrase_parse(value, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    """
    TODO: Does not support operators
    """
    splitter = next((s for s in ["-", " "]
                     if s in value), None)
    if splitter:
        buff = value.split(splitter)
        yield next(orth_parse(buff[0], config=config, op=ExtendedOp()))
        for b in buff[1:]:
            if splitter != " ":
                yield next(orth_parse(splitter, config=config, op=ExtendedOp()))
            yield next(orth_parse(b, config=config, op=ExtendedOp()))
    else:
        yield next(orth_parse(value, config=config, op=ExtendedOp()))


def tag_parse(values, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    """
    For generating POS/TAG patterns based on a Regex
    e.g. TAG("^NN|^JJ") for adjectives or nouns
    also deals with TAG_WORD for tag and word or tag and list
    """
    d = {"TAG": {"REGEX": values["tag"]}}
    if "word" in values:
        if op.ignore_case(config):
            d["LOWER"] = values["word"].lower()
        else:
            d["TEXT"] = values["word"]
    elif "list" in values:
        lst = values["list"]
        if op.ignore_case(config):
            normalized = sorted([item.lower()
                                 for item in lst])
            d["LOWER"] = {"REGEX": r"^({0})$".format("|".join(normalized))}
        else:
            d["TEXT"] = {"REGEX": r"^({0})$".format("|".join(sorted(lst)))}
    if not op.empty():
        d["OP"] = op.value
    yield d


def nested_parse(values, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    from rita.macros import resolve_value
    results = rules_to_patterns("", [resolve_value(v, config=config)
                                     for v in values], config=config)
    return results["pattern"]


def orth_parse(value, config: "SessionConfig", op: ExtendedOp) -> SpacyPattern:
    d = {}
    print(op.case_sensitive_override)
    if op.ignore_case(config):
        d["LOWER"] = value.lower()
    else:
        d["ORTH"] = value

    if not op.empty():
        d["OP"] = op.value
    yield d


PARSERS: Mapping[str, ParseFn] = {
    "any_of": any_of_parse,
    "any": any_parse,
    "value": orth_parse,
    "regex": regex_parse,
    "entity": entity_parse,
    "lemma": partial(generic_parse, "LEMMA"),
    "pos": partial(generic_parse, "POS"),
    "punct": punct_parse,
    "fuzzy": fuzzy_parse,
    "phrase": phrase_parse,
    "tag": tag_parse,
    "nested": nested_parse,
    "orth": orth_parse,
}


def rules_to_patterns(label: str, data: Patterns, config: "SessionConfig"):
    logger.debug(data)
    return {
        "label": label,
        "pattern": [p
                    for (t, d, op) in data
                    for p in PARSERS[t](d, config, ExtendedOp(op))],
    }


def compile_rules(rules: Rules, config: "SessionConfig", **kwargs):
    logger.info("Using spaCy rules implementation")
    return [rules_to_patterns(label, patterns, config=config)
            for (label, patterns) in rules]
