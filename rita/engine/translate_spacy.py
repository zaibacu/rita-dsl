import logging

from functools import partial

logger = logging.getLogger(__name__)


def any_of_parse(lst, config, op=None):
    if config.ignore_case:
        normalized = sorted([item.lower()
                             for item in lst])
        base = {"LOWER": {"REGEX": r"^({0})$".format("|".join(normalized))}}
    else:
        base = {"TEXT": {"REGEX": r"^({0})$".format("|".join(sorted(lst)))}}

    if op:
        base["OP"] = op
    yield base


def regex_parse(r, config, op=None):
    if config.ignore_case:
        d = {"LOWER": {"REGEX": r.lower()}}
    else:
        d = {"TEXT": {"REGEX": r}}

    if op:
        d["OP"] = op
    yield d


def fuzzy_parse(r, config, op=None):
    # TODO: build premutations
    d = {"LOWER": {"REGEX": "({0})[.,?;!]?".format("|".join(r))}}
    if op:
        d["OP"] = op
    yield d


def generic_parse(tag, value, config, op=None):
    d = {}
    if tag == "ORTH" and config.ignore_case:
        d["LOWER"] = value.lower()
    else:
        d[tag] = value

    if op:
        d["OP"] = op
    yield d


def punct_parse(_, config, op=None):
    d = {}
    d["IS_PUNCT"] = True
    if op:
        d["OP"] = op
    yield d


def phrase_parse(value, config, op=None):
    """
    TODO: Does not support operators
    """
    splitter = next((s for s in ["-", " "]
                     if s in value), None)
    if splitter:
        buff = value.split(splitter)
        yield next(generic_parse("ORTH", buff[0], config=config, op=None))
        for b in buff[1:]:
            if splitter != " ":
                yield next(generic_parse("ORTH", splitter, config=config, op=None))
            yield next(generic_parse("ORTH", b, config=config, op=None))
    else:
        yield generic_parse("ORTH", value, config=config, op=None)


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


def rules_to_patterns(label, data, config):
    logger.debug(data)
    return {
        "label": label,
        "pattern": [p
                    for (t, d, op) in data
                    for p in PARSERS[t](d, config=config, op=op)],
    }


def compile_rules(rules, config):
    logger.info("Using spaCy rules implementation")
    return [rules_to_patterns(*group, config=config)
            for group in rules]
