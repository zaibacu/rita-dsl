import logging

from functools import partial

from rita.utils import Node

logger = logging.getLogger(__name__)


def any_of_parse(lst, op=None):
    base = {"LOWER": {"REGEX": r"({0})".format("|".join(sorted(lst)))}}
    if op:
        base["OP"] = op
    yield base


def regex_parse(r, op=None):
    d = {"TEXT": {"REGEX": r}}

    if op:
        d["OP"] = op
    yield d


def fuzzy_parse(r, op=None):
    # TODO: build premutations
    d = {"LOWER": {"REGEX": "({0})[.,?;!]?".format("|".join(r))}}
    if op:
        d["OP"] = op
    yield d


def generic_parse(tag, value, op=None):
    d = {}
    d[tag] = value
    if op:
        d["OP"] = op
    yield d

def punct_parse(_, op=None):
    d = {}
    d["IS_PUNCT"] = True
    if op:
        d["OP"] = op
    yield d

def phrase_parse(value, op=None):
    """
    TODO: Does not support operators
    """
    buff = value.split("-")
    yield next(generic_parse("ORTH", buff[0], None))
    for b in buff[1:]:
        yield next(generic_parse("ORTH", "-", None))
        yield next(generic_parse("ORTH", b, None))


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
}


def rules_to_patterns(label, data):
    return {
        "label": label,
        "pattern": [p
                    for (t, d, op) in data
                    for p in PARSERS[t](d, op)],
    }


def compile_rules(rules):
    logger.info("Using spaCy rules implementation")
    return [rules_to_patterns(*group)
            for group in rules]
