import logging

from functools import partial

from rita.utils import ExtendedOp

logger = logging.getLogger(__name__)


def any_of_parse(lst, config, op):
    if op.ignore_case(config):
        normalized = sorted([item.lower()
                             for item in lst])
        base = {"LOWER": {"REGEX": r"^({0})$".format("|".join(normalized))}}
    else:
        base = {"TEXT": {"REGEX": r"^({0})$".format("|".join(sorted(lst)))}}

    if not op.empty():
        base["OP"] = op.value
    yield base


def regex_parse(r, config, op):
    if op.ignore_case(config):
        d = {"LOWER": {"REGEX": r.lower()}}
    else:
        d = {"TEXT": {"REGEX": r}}

    if not op.empty():
        d["OP"] = op.value
    yield d


def fuzzy_parse(r, config, op):
    # TODO: build premutations
    d = {"LOWER": {"REGEX": "({0})[.,?;!]?".format("|".join(r))}}
    if not op.empty():
        d["OP"] = op.value
    yield d


def generic_parse(tag, value, config, op):
    d = {}
    if tag == "ORTH" and op.ignore_case(config):
        d["LOWER"] = value.lower()
    else:
        d[tag] = value

    if not op.empty():
        d["OP"] = op.value
    yield d


def punct_parse(_, config, op=None):
    d = dict()
    d["IS_PUNCT"] = True
    if not op.empty():
        d["OP"] = op.value
    yield d


def phrase_parse(value, config, op):
    """
    TODO: Does not support operators
    """
    splitter = next((s for s in ["-", " "]
                     if s in value), None)
    if splitter:
        buff = value.split(splitter)
        yield next(generic_parse("ORTH", buff[0], config=config, op=ExtendedOp()))
        for b in buff[1:]:
            if splitter != " ":
                yield next(generic_parse("ORTH", splitter, config=config, op=ExtendedOp()))
            yield next(generic_parse("ORTH", b, config=config, op=ExtendedOp()))
    else:
        yield generic_parse("ORTH", value, config=config, op=ExtendedOp())


def tag_parse(values, config, op):
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


def nested_parse(values, config, op):
    from rita.macros import resolve_value
    results = rules_to_patterns("", [resolve_value(v, config=config)
                                     for v in values], config=config)
    return results["pattern"]


def orth_parse(value, config, op):
    d = {}
    d["ORTH"] = value
    if not op.empty():
        d["OP"] = op.value
    yield d


PARSERS = {
    "any_of": any_of_parse,
    "value": partial(generic_parse, "ORTH"),
    "regex": regex_parse,
    "entity": partial(generic_parse, "ENT_TYPE"),
    "lemma": partial(generic_parse, "LEMMA"),
    "pos": partial(generic_parse, "POS"),
    "punct": punct_parse,
    "fuzzy": fuzzy_parse,
    "phrase": phrase_parse,
    "tag": tag_parse,
    "nested": nested_parse,
    "orth": orth_parse,
}


def rules_to_patterns(label, data, config):
    logger.debug(data)
    return {
        "label": label,
        "pattern": [p
                    for (t, d, op) in data
                    for p in PARSERS[t](d, config=config, op=op)],
    }


def compile_rules(rules, config, **kwargs):
    logger.info("Using spaCy rules implementation")
    return [rules_to_patterns(*group, config=config)
            for group in rules]
