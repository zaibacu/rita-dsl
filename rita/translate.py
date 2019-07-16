import logging

from functools import partial

logger = logging.getLogger(__name__)


def any_of_parse(lst, op=None):
    d = {"TEXT": {"REGEX": r"({})".format("|".join(lst))}}
    if op:
        d["OP"] = op
    return d


def regex_parse(r, op=None):
    d = {"TEXT": {"REGEX": r}}

    if op:
        d["OP"] = op
    return d


def fuzzy_parse(r, op=None):
    # TODO: build premutations
    d = {"LOWER": {"REGEX": "({0})[.,?;!]?".format("|".join(r))}}
    if op:
        d["OP"] = op
    return d


def generic_parse(tag, value, op=None):
    d = {}
    d[tag] = value
    if op:
        d["OP"] = op
    return d


PARSERS = {
    "any_of": any_of_parse,
    "value": partial(generic_parse, "ORTH"),
    "regex": regex_parse,
    "entity": partial(generic_parse, "ENT_TYPE"),
    "lemma": partial(generic_parse, "LEMMA"),
    "pos": partial(generic_parse, "POS"),
    "punct": partial(generic_parse, "PUNCT"),
    "fuzzy": fuzzy_parse,
}


def rules_to_patterns(rule):
    if rule:
        logger.info(rule)
        yield {
            "label": rule["label"],
            "pattern": [PARSERS[t](d, op) for (t, d, op) in rule["data"]],
        }
